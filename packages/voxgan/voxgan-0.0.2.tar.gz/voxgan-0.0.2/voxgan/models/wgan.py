"""WGAN-style architectures"""

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
from .loss import WGANLoss, WGANGradientPenalty


################################################################################
# WGAN

class WGAN3d(BaseGAN):
    """
    Wasserstein Generative Adversarial Network (WGAN).
    
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
    output_label : str, optional (default 'WGAN')
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
    Arjovsky, M., Chintala, S. & Bottou, L. (2017).
        Wasserstein GAN.
        arXiv preprint arXiv:1701.07875, https://arxiv.org/abs/1701.07875
    Arjovsky, M. (2017).
        Wasserstein GAN.
        https://github.com/martinarjovsky/WassersteinGAN
    """
    def __init__(self,
                 size_latent_vector=100,
                 num_filters_generator=64,
                 num_filters_discriminator=64,
                 num_channels=1,
                 num_layers=4,
                 rand_labels=None,
                 output_dir_path='.',
                 output_label='WGAN',
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
                                        last_activation=None)

        super(WGAN3d, self).__init__(generator, discriminator, rand_labels,
                                     output_dir_path, output_label, verbose,
                                     num_gpus, num_nodes, distributed, backend,
                                     use_amp_training)

    def configure(self,
                  learning_rate=0.00005,
                  clamp_bounds=(-0.01, 0.01),
                  num_iter_discriminator=5):
        """
        Configures the GAN for training.
        
        Parameters
        ----------
        learning_rate : float or array-like, optional (default 0.00005)
            Learning rate for the generator and the discriminator.
        clamp_bounds : float or array-like, optional (default (-0.01, 0.01) )
            Bounds to clamp the weights of the discriminator. If a float, the
            bounds become (-clamp_bounds, clamp_bounds).
        num_iter_discriminator : int, optional (default 5)
            Number of consecutive iterations of the discriminator before an 
            iteration of the generator.
        """
        if isinstance(learning_rate, (int, float)):
            learning_rate = (learning_rate, learning_rate)

        optimizer_generator = optim.RMSprop(self.generator_.parameters(),
                                            lr=learning_rate[0])
        optimizer_discriminator = optim.RMSprop(self.discriminator_.parameters(),
                                                lr=learning_rate[1])

        loss_generator = WGANLoss()
        loss_discriminator = WGANLoss()

        fake_label_generator = 1.
        real_label_discriminator = 1.
        fake_label_discriminator = -1.

        super(WGAN3d, self).configure(optimizer_generator,
                                      optimizer_discriminator,
                                      loss_generator,
                                      loss_discriminator,
                                      num_iter_discriminator=num_iter_discriminator,
                                      fake_label_generator=fake_label_generator,
                                      real_label_discriminator=real_label_discriminator,
                                      fake_label_discriminator=fake_label_discriminator,
                                      clamp_bounds=clamp_bounds)


################################################################################
# WGAN-GP

class WGANGP3d(BaseGAN):
    """
    Wasserstein Generative Adversarial Network with Gradient Penalty (WGAN-GP).
    
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
    output_label : str, optional (default 'WGANGP')
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
    Gulrajani, I., Ahmed, F., Arjovsky, M., Dumoulin, V. & Courville, A. (2017).
        Improved Training of Wasserstein GANs.
        arXiv preprint arXiv:1704.00028, https://arxiv.org/abs/1704.00028
    Gulrajani, I. (2017).
        Code for reproducing experiments in "Improved Training of Wasserstein GANs".
        https://github.com/igul222/improved_wgan_training
    """
    def __init__(self,
                 size_latent_vector=100,
                 num_filters_generator=64,
                 num_filters_discriminator=64,
                 num_channels=1,
                 num_layers=4,
                 rand_labels=None,
                 output_dir_path='.',
                 output_label='WGANGP',
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
                                        last_activation=None)

        super(WGANGP3d, self).__init__(generator, discriminator, rand_labels,
                                       output_dir_path, output_label, verbose,
                                       num_gpus, num_nodes, distributed, backend,
                                       use_amp_training)

    def configure(self,
                  learning_rate=0.0001,
                  beta1=0.5,
                  gamma=10.,
                  num_iter_discriminator=5):
        """
        Configures the GAN for training.
        
        Parameters
        ----------
        learning_rate : float or array-like, optional (default 0.0001)
            Learning rate for the generator and the discriminator.
        beta1 : float or array-like, optional (default 0.5)
            Beta_1 parameter for the generator and the discriminator.
        gamma : float, optional (default 10)
            Weight of the gradient penalty.
        num_iter_discriminator : int, optional (default 5)
            Number of consecutive iterations of the discriminator before an 
            iteration of the generator.
        """
        if isinstance(learning_rate, (int, float)):
            learning_rate = (learning_rate, learning_rate)
        if isinstance(beta1, (int, float)):
            beta1 = (beta1, beta1)

        optimizer_generator = optim.Adam(self.generator_.parameters(),
                                         lr=learning_rate[0],
                                         betas=(beta1[0], 0.9))
        optimizer_discriminator = optim.Adam(self.discriminator_.parameters(),
                                             lr=learning_rate[1],
                                             betas=(beta1[1], 0.9))

        loss_generator = WGANLoss()
        loss_discriminator = WGANLoss()
        penalty_discriminator = WGANGradientPenalty(gamma=gamma)

        fake_label_generator = 1.
        real_label_discriminator = 1.
        fake_label_discriminator = -1.

        super(WGANGP3d, self).configure(optimizer_generator,
                                        optimizer_discriminator,
                                        loss_generator,
                                        loss_discriminator,
                                        num_iter_discriminator=num_iter_discriminator,
                                        fake_label_generator=fake_label_generator,
                                        real_label_discriminator=real_label_discriminator,
                                        fake_label_discriminator=fake_label_discriminator,
                                        penalty_discriminator=penalty_discriminator)
