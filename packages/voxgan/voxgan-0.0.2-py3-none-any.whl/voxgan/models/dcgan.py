"""DCGAN-style architectures"""

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


from functools import partial

import torch.nn as nn
import torch.optim as optim

from .base import BaseGAN
from ..networks.dcgan import Generator3d, Discriminator3d


################################################################################
# DCGAN

class DCGAN3d(BaseGAN):
    """
    Deep Convolutional Generative Adversarial Network (DCGAN).
    
    Parameters
    ----------
    size_latent_vector : int, optional (default 100)
        Length of the latent vector.
    num_filters_generator : int, optional (default 64)
        Initial number of filters for the convolution of the generator.
    num_filters_discriminator : int, optional (default 64)
        Initial number of filters for the convolution of the discriminator.
    num_channels : int, optional (default 1)
        Number of channels in the output images.
    num_layers : int or tuple, optional (default 4)
        Number of layers of the generator and discriminator. By default,
        generates 64 x 64 x 64 images.
    rand_labels : function, optional (default None)
        Function to generate random labels when generating samples. It's only
        input should be a batch size.
    output_dir_path : str, optional (default '.')
        Path to the directory in which checkpoints and samples are saved.
    output_label : str, optional (default 'GAN')
        Label to add to the name of the files saved in save_directory.
    verbose : int, optional (default 1)
        Level of verbosity. 0 means nothing is printed, 1 means some information
        is printed at epoch level, 2 means some information is printed at batch
        level.
    num_gpus : int, optional (default 1)
        Number of GPUs available. If this is 0, code will run in CPU mode. If 
        this number is greater than 0 it will run on that number of GPUs.
    num_nodes : int, optional (default 1)
        Number of nodes available.
    distributed : bool, optional (default False)
        If true, uses distributed data parallelism.
    backend : str, optional (default 'gloo')
        Backend to use for distributed data parallelism. Valid values include
        `mpi`, `gloo`, and `nccl`.
    use_amp_training : bool, optional (default False)
        If True, uses automatic mixed precision training.

    Attributes
    ----------
    generator_ : nn.Module
        PyTorch model for the generator.
    discriminator_ : nn.Module
        PyTorch model for the discriminator.
    history_ : defaultdict
        Store the training history, e.g., epoch, batch number, losses, metrics.
    
    References
    ----------
    Radford, A., Metz, L., & Chintala, S. (2016).
        Unsupervised Representation Learning with Deep Convolutional Generative Adversarial Networks.
        arXiv preprint arXiv:1511.06434, https://arxiv.org/abs/1511.06434
    Inkawhich, N. (2017).
        DCGAN Tutorial.
        PyTorch Tutorials, https://pytorch.org/tutorials/beginner/dcgan_faces_tutorial.html  
    """
    def __init__(self,
                 size_latent_vector=100,
                 num_filters_generator=64,
                 num_filters_discriminator=64,
                 num_channels=1,
                 num_layers=4,                 
                 rand_labels=None,
                 output_dir_path='.',
                 output_label='DCGAN',
                 verbose=1,
                 num_gpus=1,
                 num_nodes=1,
                 distributed=False,
                 backend='gloo',
                 use_amp_training=False):

        generator = Generator3d(nz=size_latent_vector,
                                ngf=num_filters_generator,
                                nc=num_channels,
                                nl=num_layers,
                                layer_normalization=nn.BatchNorm3d,
                                activation=partial(nn.ReLU, inplace=True),
                                last_activation=nn.Tanh)
        discriminator = Discriminator3d(ndf=num_filters_discriminator,
                                        nc=num_channels,
                                        nl=num_layers,
                                        layer_normalization=nn.BatchNorm3d,
                                        activation=partial(nn.LeakyReLU, negative_slope=0.2, inplace=True),
                                        last_activation=nn.Sigmoid)

        super(DCGAN3d, self).__init__(generator, discriminator, rand_labels,
                                      output_dir_path, output_label, verbose,
                                      num_gpus, num_nodes, distributed, backend,
                                      use_amp_training)

    def configure(self,
                  learning_rate=0.0002,
                  beta1=0.5,
                  num_iter_discriminator=1,
                  real_label_discriminator=1.):
        """
        Configures the GAN for training.
        
        Parameters
        ----------
        learning_rate : float or array-like, optional (default 0.0002)
            Learning rate for the generator and the discriminator.
        beta1 : float or array-like, optional (default 0.5)
            Beta_1 parameter for the generator and the discriminator.
        num_iter_discriminator : int, optional (default 1)
            Number of consecutive iterations of the discriminator before an 
            iteration of the generator.
        real_label_discriminator : float, optional (default 1)
            Target label of the real data for the discriminator.
        """
        if isinstance(learning_rate, (int, float)):
            learning_rate = (learning_rate, learning_rate)
        if isinstance(beta1, (int, float)):
            beta1 = (beta1, beta1)

        optimizer_generator = optim.Adam(self.generator_.parameters(),
                                         lr=learning_rate[0],
                                         betas=(beta1[0], 0.999))
        optimizer_discriminator = optim.Adam(self.discriminator_.parameters(),
                                             lr=learning_rate[1],
                                             betas=(beta1[1], 0.999))

        loss_generator = nn.BCELoss()
        loss_discriminator = nn.BCELoss()

        super(DCGAN3d, self).configure(optimizer_generator,
                                       optimizer_discriminator,
                                       loss_generator,
                                       loss_discriminator,
                                       num_iter_discriminator=num_iter_discriminator,
                                       real_label_discriminator=real_label_discriminator)
