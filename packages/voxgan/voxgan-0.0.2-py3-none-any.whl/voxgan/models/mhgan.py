"""Metropolis-Hastings Generative Adversarial Network"""

# MIT License

# Copyright (c) 2021-2025 Guillaume Rongier
# Copyright (c) 2020-2021 Commonwealth Scientific and Industrial Research Organisation (CSIRO) ABN 41 687 119 230

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Copyright notice: See `LICENSE.md` for more information.


import numpy as np

import torch
from torch.utils.data import DataLoader, ConcatDataset
from sklearn.calibration import CalibratedClassifierCV

from ..data.datasets import DictDataset
from ..models.base import move_to, detach


################################################################################
# Generative Adversarial Network

class MHGAN:
    """
    Base class to train Metropolis-Hastings Generative Adversarial Networks (MHGANs)
    from already trained Generative Adversarial Networks (GANs).
    
    Parameters
    ----------
    generator : nn.Module
        Trained PyTorch model for the generator of the GAN.
    discriminator : nn.Module
        Trained PyTorch model for the discriminator of the GAN.
    calibration : str, optional (default 'isotonic')
        Method to use for calibration, either 'isotonic' or 'sigmoid'.
    rand_labels : function, optional (default None)
        Function to generate random labels when generating samples. It's only
        input should be a batch size.
    verbose : int, optional (default 1)
        Level of verbosity. 0 means nothing is printed, 1 means some information
        is printed at chain level, 2 means some information is printed at
        acceptance level.
    num_gpus : int, optional (default 1)
        Number of GPUs available. If this is 0, code will run in CPU mode. If 
        this number is greater than 0 it will run on that number of GPUs.

    References
    ----------
    Turner, R., Hung, J., Frank, E., Saatci, Y., Yosinski, J. (2018).
        Metropolis-Hastings Generative Adversarial Networks.
        arXiv preprint arXiv:1811.11357, https://arxiv.org/abs/1811.11357
    """
    def __init__(self,
                 generator,
                 discriminator,
                 calibration='isotonic',
                 rand_labels=None,
                 verbose=1,
                 num_gpus=1):

        self.verbose = verbose

        self._device = torch.device('cuda:0' if (torch.cuda.is_available() and num_gpus > 0) else 'cpu')
        self.generator = generator.to(self._device)
        self.discriminator = discriminator.to(self._device)
        self.calibration = calibration
        self.rand_labels = rand_labels

    def _predict(self, num_samples=1, batch_size=1, latent_shape=None):
        """
        Simulate realizations using the generator.
        
        Parameters
        ----------
        num_samples : int, optional (default 1)
            Number of samples to generate.
        batch_size : int, optional (default 1)
            Number of realizations per batch to simulate.
        latent_shape : array-like, optional (default None)
            Shape of the latent vector to simulate realizations larger than the
            training shape. 1 along each dimension by default.

        Returns
        -------
        predictions : array, shape (num_samples, num_channels, height, width, depth)
            Realizations from the generator.
        """
        if latent_shape is None:
            latent_shape = self.latent_shape

        self.generator.eval()

        with torch.no_grad():
            predictions = {'data': []}
            if self.rand_labels is not None:
                predictions['labels'] = []
            for i in range(0, num_samples, batch_size):
                b_size = min(batch_size, num_samples - i)
                noise = {'data': torch.randn(b_size, self.generator.nz, *latent_shape, device=self._device)}
                if self.rand_labels is not None:
                    noise['labels'] = self.rand_labels(b_size).to(self._device)
                prediction = detach(self.generator(noise))
                predictions['data'].append(prediction['data'])
                if self.rand_labels is not None:
                    predictions['labels'].append(prediction['labels'])
            for key in predictions:
                predictions[key] = torch.cat(predictions[key], dim=0).cpu()

            return predictions

    def fit(self, dataset, batch_size=128, num_workers=1):
        """
        Calibrates the discriminator to get well-calibrated probabilities.
        
        Parameters
        ----------
        dataset : Dataset
            PyTorch dataset giving access to the data for calibration. Those
            data should not be part of the dataset used to train the generator
            and discriminator.
        batch_size : int, optional (default 128)
            Number of samples per batch to load.
        num_workers : int, optional (default 1)
            Number of subprocesses to use for data loading. 0 means that the
            data will be loaded in the main process.
        """
        if self.verbose > 0:
            print("Starting calibration...")

        if isinstance(dataset[0], (tuple, list)):
            nb_dims = len(dataset[0][0]['data'].shape) - 1
        else:
            nb_dims = len(dataset[0]['data'].shape) - 1
        self.latent_shape = (1,)*nb_dims
        
        self.calibrator = CalibratedClassifierCV(method=self.calibration)

        fake_samples = self._predict(len(dataset), batch_size=batch_size)
        fake_set = DictDataset(fake_samples)

        merged_set = ConcatDataset((dataset, fake_set))
        merged_loader = DataLoader(merged_set,
                                   batch_size=batch_size,
                                   shuffle=False,
                                   num_workers=num_workers,
                                   drop_last=False)

        scores = []
        for batch in merged_loader:
            batch = move_to(batch, self._device)
            score = self.discriminator(batch)['data'].detach()
            scores.append(score)
        scores = torch.cat(scores).cpu().numpy()

        scores_true = np.concatenate((np.ones(len(dataset), dtype=np.float32),
                                      np.zeros(len(dataset), dtype=np.float32)))

        self.calibrator.fit(scores.reshape(-1, 1), scores_true)

        if self.verbose > 0:
            print("Ending calibration...")

    def discriminate(self, samples):
        """
        Tells whether some samples are real using the calibrated disciminator.
        
        Parameters
        ----------
        samples : tensor of shape ([num_samples], num_channels, height, width, depth)
            Sample(s) to discriminate.
            
        Returns
        -------
        predict_proba : float
            Probabilities that the samples are real.
        """
        # if len(samples.shape) == len(self.latent_shape) + 1:
        #     samples = samples[None]
        samples = move_to(samples, self._device)

        scores = self.discriminator(samples)['data'].detach().cpu().numpy()

        return self.calibrator.predict_proba(scores.reshape(-1, 1))[:, 1].squeeze()
    
    def _accept_proba(self, accept_errD, errD):
        """
        Computes the probability of accepting a samples in a chain.
        """
        if accept_errD > 0. and errD > 0. and errD < 1.:
            return min(1., (1./accept_errD - 1.)/(1./errD - 1.))
        else:
            return 1.

    def _mh_predict(self, latent_shape, nb_chain_samples, init_dataset=None):
        """
        Generate samples using the Metropolis-Hastings method.
        """
        init_sample = None
        if init_dataset is not None:
            idx = np.random.randint(len(init_dataset))
            init_sample = init_dataset[idx]
            # if isinstance(init_sample, (tuple, list)):
            #     init_sample = init_sample[0]
            init_sample = init_sample[None].to(self._device)
        else:
            init_sample = self._predict(latent_shape=latent_shape)
        init_errD = self.discriminate(init_sample)
        if self.verbose > 1:
            print("... Initial sample is real?", init_errD)

        accept_sample = init_sample
        accept_errD = init_errD
        for k in range(0, nb_chain_samples):
            sample = self._predict(latent_shape=latent_shape)
            errD = self.discriminate(sample)
            accept_proba = self._accept_proba(accept_errD, errD)
            if np.random.rand() <= accept_proba:
                accept_errD = errD
                accept_sample = sample
                if self.verbose > 1:
                    print("... Iteration ", k + 1,
                          ": New accepted sample is real? ", accept_errD, sep="")
                
        is_identical = True
        for key in init_sample:
            if torch.eq(accept_sample[key], init_sample[key]).all() == False:
                is_identical = False
        if is_identical == True and init_dataset is not None:
            if self.verbose > 0:
                print("... Final sample is the same as initial sample...\n",
                      "... Restarting the chain with a random initial sample...")
            accept_sample = self._mh_predict(latent_shape,
                                             nb_chain_samples,
                                             init_dataset=None)

        return accept_sample

    def predict(self,
                num_samples=1,
                num_chain_samples=640,
                init_dataset=None,
                latent_shape=None):
        """
        Generates samples in MCMC chains.
        
        Parameters
        ----------
        num_samples : int, optional (default 1)
            Number of samples to generate.
        num_chain_samples : int, optional (default 640)
            Number of samples that each chain has to generate.
        init_dataset : Dataset
            PyTorch dataset giving access to the data to initiate the chains.
        latent_shape : array-like, optional (default None)
            Shape of the latent vector to simulate realizations larger than the
            training shape. 1 along each dimension by default.

        Returns
        -------
        samples : array, shape (num_samples, num_channels, height, width, depth)
            Final samples from the MCMC chains.
        """
        if latent_shape is None:
            latent_shape = self.latent_shape

        self.generator.eval()

        with torch.no_grad():
            samples = {'data': []}
            if self.rand_labels is not None:
                samples['labels'] = []
            for i in range(0, num_samples):
                if self.verbose > 0:
                    print("Chain ", i + 1, "...", sep="")
                    sample = self._mh_predict(latent_shape,
                                              num_chain_samples,
                                              init_dataset=init_dataset)
                    samples['data'].append(sample['data'])
                    if self.rand_labels is not None:
                        samples['labels'].append(sample['labels'])
            for key in samples:
                samples[key] = torch.cat(samples[key], dim=0).cpu()

            return samples
