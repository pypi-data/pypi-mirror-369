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
from torch.nn.modules.utils import _triple

from .base import *
from .blocks import *


################################################################################
# 2D

class Generator2d(BaseGenerator):
    """
    DCGAN generator for 2D images of size 64*64.
    
    Parameters
    ----------
    nz : int, optional (default 100)
        Length of the latent vector.
    ngf : int, optional (default 64)
        Initial number of filters for the convolution.
    nc : int, optional (default 1)
        Number of channels in the output images.
    layer_normalization : nn.Module, optional (default nn.BatchNorm2d)
        Normalization to apply to the output of the convolution (e.g., batch
        normalization).
    weight_normalization : function, optional (default None)
        Normalization to apply to the weights of the convolution (e.g., spectral
        normalization).
    activation : nn.Module, optional (default nn.ReLU)
        Activation to apply after the convolutions and normalizations.
    last_activation : nn.Module, optional (default nn.Tanh)
        Activation to apply at the very end.
    embedding : nn.Module, optional (default None)
        Label embedding.
    ne : int, optional (default 200)
        Size of the dictionary of embeddings.
    nd : int, optional (default 128)
        Size of each embedding vector.
    """
    def __init__(self,
                 nz=100,
                 ngf=64,
                 nc=1,
                 layer_normalization=nn.BatchNorm2d,
                 weight_normalization=None,
                 activation=partial(nn.ReLU, inplace=True),
                 last_activation=nn.Tanh,
                 embedding=None,
                 ne=200,
                 nd=128):

        super(Generator2d, self).__init__(nz, embedding, ne, nd)

        self.main = nn.Sequential(
            # input is Z, going into a convolution
            ConvBlockTranspose2d(nz + self.ne, ngf*8, 4, 1, 0, bias=False, layer_normalization=layer_normalization, weight_normalization=weight_normalization, activation=activation),
             # state size. (ngf*8) x 4 x 4
            ConvBlockTranspose2d(ngf*8, ngf*4, 4, 2, 1, bias=False, layer_normalization=layer_normalization, weight_normalization=weight_normalization, activation=activation),
            # state size. (ngf*4) x 8 x 8
            ConvBlockTranspose2d(ngf*4, ngf*2, 4, 2, 1, bias=False, layer_normalization=layer_normalization, weight_normalization=weight_normalization, activation=activation),
            # state size. (ngf*2) x 16 x 16
            ConvBlockTranspose2d(ngf*2, ngf, 4, 2, 1, bias=False, layer_normalization=layer_normalization, weight_normalization=weight_normalization, activation=activation),
            # state size. (ngf) x 32 x 32
            ConvBlockTranspose2d(ngf, nc, 4, 2, 1, bias=False, layer_normalization=None, weight_normalization=weight_normalization, activation=last_activation)
            # state size. (nc) x 64 x 64
        )


class Discriminator2d(BaseDiscriminator):
    """
    DCGAN discriminator for 2D images of size 64*64.
    
    Parameters
    ----------
    ndf : int, optional (default 64)
        Initial number of filters for the convolution.
    nc : int, optional (default 1)
        Number of channels in the output images.
    layer_normalization : nn.Module, optional (default nn.BatchNorm2d)
        Normalization to apply to the output of the convolution (e.g., batch
        normalization).
    weight_normalization : function, optional (default None)
        Normalization to apply to the weights of the convolution (e.g., spectral
        normalization).
    activation : nn.Module, optional (default nn.LeakyReLU)
        Activation to apply after the convolutions and normalizations.
    last_activation : nn.Module, optional (default nn.Sigmoid)
        Activation to apply at the very end.
    embedding : nn.Module, optional (default None)
        Label embedding.
    ne : int, optional (default 200)
        Size of the dictionary of embeddings.
    nd : int, optional (default 128)
        Size of each embedding vector.
    """
    def __init__(self,
                 ndf=64,
                 nc=1,
                 layer_normalization=nn.BatchNorm2d,
                 weight_normalization=None,
                 activation=partial(nn.LeakyReLU, negative_slope=0.2, inplace=True),
                 last_activation=nn.Sigmoid,
                 embedding=None,
                 ne=200,
                 nd=128):

        super(Discriminator2d, self).__init__(embedding, ne, nd)

        self.main = nn.Sequential(
            # input is (nc) x 64 x 64
            ConvBlock2d(nc, ndf, 4, 2, 1, bias=False, layer_normalization=None, weight_normalization=weight_normalization, activation=activation),
            # state size. (ndf) x 32 x 32
            ConvBlock2d(ndf, ndf*2, 4, 2, 1, bias=False, layer_normalization=layer_normalization, weight_normalization=weight_normalization, activation=activation),
            # state size. (ndf*2) x 16 x 16
            ConvBlock2d(ndf*2, ndf*4, 4, 2, 1, bias=False, layer_normalization=layer_normalization, weight_normalization=weight_normalization, activation=activation),
            # state size. (ndf*4) x 8 x 8
            ConvBlock2d(ndf*4, ndf*8, 4, 2, 1, bias=False, layer_normalization=layer_normalization, weight_normalization=weight_normalization, activation=activation),
            # state size. (ndf*8) x 4 x 4
            ConvBlock2d(ndf*8, 1 + self.ne, 4, 1, 0, bias=False, layer_normalization=None, weight_normalization=weight_normalization, activation=last_activation)
        )


################################################################################
# 3D

class Generator3d(BaseGenerator):
    """
    DCGAN generator for 3D images.
    
    Parameters
    ----------
    nz : int, optional (default 100)
        Length of the latent vector.
    ngf : int, optional (default 64)
        Initial number of filters for the convolution.
    nc : int, optional (default 1)
        Number of channels in the output images.
    nl : int or tuple, optional (default 4)
        Number of layers. By default, generates 64 x 64 x 64 images.
    max_factor : int, optional (default 16)
        Maximum factor to apply to ndf in the successive layers.
    layer_normalization : nn.Module, optional (default nn.BatchNorm3d)
        Normalization to apply to the output of the convolution (e.g., batch
        normalization).
    weight_normalization : function, optional (default None)
        Normalization to apply to the weights of the convolution (e.g., spectral
        normalization).
    activation : nn.Module, optional (default nn.ReLU)
        Activation to apply after the convolutions and normalizations.
    last_activation : nn.Module, optional (default nn.Tanh)
        Activation to apply at the very end.
    embedding : nn.Module, optional (default None)
        Label embedding.
    ne : int, optional (default 200)
        Size of the dictionary of embeddings.
    nd : int, optional (default 128)
        Size of each embedding vector.
    """
    def __init__(self,
                 nz=100,
                 ngf=64,
                 nc=1,
                 nl=4,
                 max_factor=16,
                 layer_normalization=nn.BatchNorm3d,
                 weight_normalization=None,
                 activation=partial(nn.ReLU, inplace=True),
                 last_activation=nn.Tanh,
                 embedding=None,
                 ne=200,
                 nd=128):

        super(Generator3d, self).__init__(nz, embedding, ne, nd)
        
        nl = _triple(nl)
        factor = 2**(max(nl) - 1)
        # input is Z, going into a convolution
        filter = [4 if j > 0 else 1 for j in nl]
        main = [ConvBlockTranspose3d(nz + self.ne, ngf*min(factor, max_factor), filter, 1, 0, bias=False, layer_normalization=layer_normalization, weight_normalization=weight_normalization, activation=activation)]
        for i in range(max(nl) - 1):
            new_factor = max(1, factor//2)
            filter = [4 if i < j and j > 0 else 1 for j in nl]
            stride = [2 if i < j and j > 0 else 1 for j in nl]
            padding = [1 if i < j and j > 0 else 0 for j in nl]
            main += [ConvBlockTranspose3d(ngf*min(factor, max_factor), ngf*min(new_factor, max_factor), filter, stride, padding, bias=False, layer_normalization=layer_normalization, weight_normalization=weight_normalization, activation=activation)]
            factor = new_factor
        filter = [4 if max(nl) == j and j > 0 else 1 for j in nl]
        stride = [2 if max(nl) == j and j > 0 else 1 for j in nl]
        padding = [1 if max(nl) == j and j > 0 else 0 for j in nl]
        main += [ConvBlockTranspose3d(ngf, nc, filter, stride, padding, bias=False, layer_normalization=None, weight_normalization=weight_normalization, activation=last_activation)]
        self.main = nn.Sequential(*main)


class Discriminator3d(BaseDiscriminator):
    """
    DCGAN discriminator for 3D images.
    
    Parameters
    ----------
    ndf : int, optional (default 64)
        Initial number of filters for the convolution.
    nc : int, optional (default 1)
        Number of channels in the output images.
    nl : int or tuple, optional (default 4)
        Number of layers. By default, generates 64 x 64 x 64 images.
    max_factor : int, optional (default 16)
        Maximum factor to apply to ndf in the successive layers.
    layer_normalization : nn.Module, optional (default nn.BatchNorm3d)
        Normalization to apply to the output of the convolution (e.g., batch
        normalization).
    weight_normalization : function, optional (default None)
        Normalization to apply to the weights of the convolution (e.g., spectral
        normalization).
    activation : nn.Module, optional (default nn.LeakyReLU)
        Activation to apply after the convolutions and normalizations.
    last_activation : nn.Module, optional (default nn.Sigmoid)
        Activation to apply at the very end.
    embedding : nn.Module, optional (default None)
        Label embedding.
    ne : int, optional (default 200)
        Size of the dictionary of embeddings.
    nd : int, optional (default 128)
        Size of each embedding vector.
    """
    def __init__(self,
                 ndf=64,
                 nc=1,
                 nl=4,
                 max_factor=16,
                 layer_normalization=nn.BatchNorm3d,
                 weight_normalization=None,
                 activation=partial(nn.LeakyReLU, negative_slope=0.2, inplace=True),
                 last_activation=nn.Sigmoid,
                 embedding=None,
                 ne=200,
                 nd=128):

        super(Discriminator3d, self).__init__(embedding, ne, nd)

        nl = _triple(nl)
        factor = 1
        filter = [4 if j > 0 else 1 for j in nl]
        stride = [2 if j > 0 else 1 for j in nl]
        padding = [1 if j > 0 else 0 for j in nl]
        main = [ConvBlock3d(nc, ndf, filter, stride, padding, bias=False, layer_normalization=None, weight_normalization=weight_normalization, activation=activation)]
        for i in range(1, max(nl)):
            new_factor = min(max_factor, factor*2)
            filter = [4 if i < j and j > 0 else 1 for j in nl]
            stride = [2 if i < j and j > 0 else 1 for j in nl]
            padding = [1 if i < j and j > 0 else 0 for j in nl]
            main += [ConvBlock3d(ndf*factor, ndf*new_factor, filter, stride, padding, bias=False, layer_normalization=layer_normalization, weight_normalization=weight_normalization, activation=activation)]
            factor = new_factor
        filter = [4 if j > 0 else 1 for j in nl]
        main += [ConvBlock3d(ndf*factor, 1 + self.ne, filter, 1, 0, bias=False, layer_normalization=None, weight_normalization=weight_normalization, activation=last_activation)]
        self.main = nn.Sequential(*main)
