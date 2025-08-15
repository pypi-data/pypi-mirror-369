"""RESNET-style architectures"""

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


import torch.nn as nn
from torch.nn.modules.utils import _triple

from .base import *
from .blocks import *
from ..models.base import copy


################################################################################
# 2D

class Generator2d(BaseGenerator):
    """
    RESNET generator for 2D images of size 64*64.
    
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
                 mode='nearest',
                 layer_normalization=nn.BatchNorm2d,
                 weight_normalization=None,
                 activation=nn.ReLU,
                 last_activation=nn.Sigmoid,
                 embedding=None,
                 ne=200,
                 nd=128):

        super(Generator2d, self).__init__(nz, embedding, ne, nd)

        main = [
            # input is Z, going into a convolution
            ConvBlockTranspose2d(nz + self.ne, ngf*8, 1, 1, 0, bias=False, layer_normalization=None, weight_normalization=None, activation=activation), # nn.Linear(nz, ngf*8*4*4)
            # state size. (ngf*8) x 4 x 4
            ResBlock2d(ngf*8, ngf*4, layer_normalization=layer_normalization, weight_normalization=weight_normalization, activation=activation),
            nn.Upsample(scale_factor=2, mode=mode),
            # state size. (ngf*4) x 8 x 8
            ResBlock2d(ngf*4, ngf*4, layer_normalization=layer_normalization, weight_normalization=weight_normalization, activation=activation),
            nn.Upsample(scale_factor=2, mode=mode),
            # state size. (ngf*4) x 16 x 16
            ResBlock2d(ngf*4, ngf*2, layer_normalization=layer_normalization, weight_normalization=weight_normalization, activation=activation),
            nn.Upsample(scale_factor=2, mode=mode),
            # state size. (ngf*2) x 32 x 32
            ResBlock2d(ngf*2, ngf, layer_normalization=layer_normalization, weight_normalization=weight_normalization, activation=activation),
            nn.Upsample(scale_factor=2, mode=mode),
            # state size. (ngf) x 64 x 64
        ]
        if layer_normalization is not None:
            main += [layer_normalization(ngf)]
        main += [activation(),
                 ConvBlock2d(ngf, nc, 7, 1, 3, bias=False, layer_normalization=None, weight_normalization=None, activation=last_activation)]
        # state size. (nc) x 64 x 64
        self.main = nn.Sequential(*main)


class Discriminator2d(BaseDiscriminator):
    """
    RESNET discriminator for 2D images of size 64*64.
    
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
                 activation=nn.ReLU,
                 last_activation=None,
                 embedding=None,
                 ne=200,
                 nd=128):

        super(Discriminator2d, self).__init__(embedding, ne, nd)

        self.main = nn.Sequential(
            # input is (nc) x 64 x 64
            ConvBlock2d(nc, ndf, 7, 1, 3, bias=False, layer_normalization=None, weight_normalization=None, activation=activation),
            nn.AvgPool2d(2),
            ResBlock2d(ndf, ndf, 2, 3, 1, 1, bias=False, layer_normalization=layer_normalization, weight_normalization=weight_normalization, activation=activation),
            # state size. (ndf) x 32 x 32
            nn.AvgPool2d(2),
            ResBlock2d(ndf, ndf*2, 2, 3, 1, 1, bias=False, layer_normalization=layer_normalization, weight_normalization=weight_normalization, activation=activation),
            # state size. (ndf*2) x 16 x 16
            nn.AvgPool2d(2),
            ResBlock2d(ndf*2, ndf*4, 2, 3, 1, 1, bias=False, layer_normalization=layer_normalization, weight_normalization=weight_normalization, activation=activation),
            # state size. (ndf*4) x 8 x 8
            nn.AvgPool2d(2),
            ResBlock2d(ndf*4, ndf*4, 2, 3, 1, 1, bias=False, layer_normalization=layer_normalization, weight_normalization=weight_normalization, activation=activation),
            # state size. (ndf*4) x 4 x 4
            nn.AvgPool2d(2),
            ResBlock2d(ndf*4, ndf*8, 2, 3, 1, 1, bias=False, layer_normalization=layer_normalization, weight_normalization=weight_normalization, activation=activation),
            # state size. (ndf*8) x 2 x 2
            activation(),
            nn.AvgPool2d(2),
            # state size. (ndf*8) x 1 x 1
            ConvBlock2d(ndf*8, 1 + self.ne, 1, 1, 0, bias=False, layer_normalization=None, weight_normalization=None, activation=last_activation)
            # state size. 1 x 1 x 1
        )


################################################################################
# 3D

class SimpleGenerator3d(BaseGenerator):
    """
    RESNET generator for 3D images.
    
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
    max_factor : int, optional (default 8)
        Maximum factor to apply to ngf in the successive layers.
    residual_weight : float, optional (default 0.1)
        Weight of the residual mapping.
    mode : str, optional (default 'nearest')
        Interpolation used for upscaling.
    kernel_size : int or tuple, optional (default 3)
        Size of the convolving kernel.
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

    References
    ----------
    Mescheder, L. (2020).
        Stability and Expressiveness of Deep Generative Models.
        PhD Thesis, Universitat Tubingen, https://hdl.handle.net/10900/106074
    """
    def __init__(self,
                 nz=256,
                 ngf=64,
                 nc=1,
                 nl=4,
                 max_factor=8,
                 residual_weight=0.1,
                 mode='nearest',
                 kernel_size=3,
                 layer_normalization=nn.BatchNorm3d,
                 weight_normalization=None,
                 activation=nn.ReLU,
                 last_activation=nn.Tanh,
                 embedding=None,
                 ne=200,
                 nd=128):

        super(SimpleGenerator3d, self).__init__(nz, embedding, ne, nd)

        nl = _triple(nl)
        factor = max(2**(max(nl) - 1), max_factor)
        filter = [4 if j > 0 else 1 for j in nl]
        # input is Z, going into a convolution
        main = [ConvBlockTranspose3d(nz + self.nd, ngf*factor, filter, 1, 0, bias=False, layer_normalization=None, weight_normalization=weight_normalization, activation=None)]
        for i in range(max(nl)):
            scale_factor = tuple([2 if i < j and j > 0 else 1 for j in nl])
            filter = [kernel_size if i < j and j > 0 else 1 for j in nl]
            padding = [kernel_size//2 if i < j and j > 0 else 0 for j in nl]
            new_factor = max(1, factor//2)
            main += [ResBlock3d(ngf*factor, ngf*new_factor, residual_weight=residual_weight, kernel_size=filter, padding=padding,
                                layer_normalization=layer_normalization, weight_normalization=weight_normalization, activation=activation),
                     nn.Upsample(scale_factor=scale_factor, mode=mode)]
            factor = new_factor
        if layer_normalization is not None:
            main += [layer_normalization(ngf)]
        main += [activation()]
        filter = [kernel_size if max(nl) == j and j > 0 else 1 for j in nl]
        padding = [kernel_size//2 if max(nl) == j and j > 0 else 0 for j in nl]
        main += [ConvBlock3d(ngf, nc, filter, 1, padding, bias=False, layer_normalization=None, weight_normalization=weight_normalization, activation=last_activation)]
        self.main = nn.Sequential(*main)


class SimpleDiscriminator3d(BaseDiscriminator):
    """
    RESNET discriminator for 3D images.
    
    Parameters
    ----------
    ndf : int, optional (default 64)
        Initial number of filters for the convolution.
    nc : int, optional (default 1)
        Number of channels in the output images.
    nl : int or tuple, optional (default 4)
        Number of layers. By default, generates 64 x 64 x 64 images.
    max_factor : int, optional (default 8)
        Maximum factor to apply to ndf in the successive layers.
    residual_weight : float, optional (default 0.1)
        Weight of the residual mapping.
    kernel_size : int or tuple, optional (default 3)
        Size of the convolving kernel.
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

    References
    ----------
    Mescheder, L. (2020).
        Stability and Expressiveness of Deep Generative Models.
        PhD Thesis, Universitat Tubingen, https://hdl.handle.net/10900/106074
    """
    def __init__(self,
                 ndf=64,
                 nc=1,
                 nl=4,
                 max_factor=8,
                 residual_weight=0.1,
                 kernel_size=3,
                 layer_normalization=nn.BatchNorm3d,
                 weight_normalization=None,
                 activation=nn.ReLU,
                 last_activation=None,
                 embedding=None,
                 ne=200,
                 nd=128):

        super(SimpleDiscriminator3d, self).__init__(embedding, ne, nd)

        nl = _triple(nl)
        factor = 1
        filter = [kernel_size if j > 0 else 1 for j in nl]
        padding = [kernel_size//2 if j > 0 else 0 for j in nl]
        main = [ConvBlock3d(nc, ndf, filter, 1, padding, bias=False, layer_normalization=None, weight_normalization=weight_normalization, activation=None)]
        for i in range(max(nl) - 1):
            scale_factor = [2 if i < j and j > 0 else 1 for j in nl]
            filter = [kernel_size if i < j and j > 0 else 1 for j in nl]
            padding = [kernel_size//2 if i < j and j > 0 else 0 for j in nl]
            new_factor = min(max_factor, factor*2)
            main += [nn.AvgPool3d(scale_factor),
                     ResBlock3d(ndf*factor, ndf*new_factor, residual_weight=residual_weight, kernel_size=filter, padding=padding,
                                layer_normalization=layer_normalization, weight_normalization=weight_normalization, activation=activation)]
            factor = new_factor
        if layer_normalization is not None:
            main += [layer_normalization(ndf*factor)]
        main += [activation()]
        scale_factor = [2 if max(nl) == j and j > 0 else 1 for j in nl]
        filter = [4 if j > 0 else 1 for j in nl]
        main += [nn.AvgPool3d(scale_factor)]
        main += [ConvBlock3d(ndf*factor, 1 + self.ne, filter, 1, 0, bias=False, layer_normalization=None, weight_normalization=weight_normalization, activation=last_activation)]
        self.main = nn.Sequential(*main)

    def forward(self, input):

        if isinstance(input, dict) == False:
            input = {'data': input}

        output_full = self.main(input['data'])
        output = {'data': output_full[:, :1].squeeze()}
        if self.embedding is not None and 'labels' in input:
            output['labels'] = self.embedding(output_full[:, 1:]).squeeze()

        return output


class Generator3d(BaseGenerator):
    """
    RESNET generator for 3D images.
    
    Parameters
    ----------
    nz : int (default 100)
        Length of the latent vector.
    ngf : int (default 64)
        Initial number of filters for the convolution.
    nc : int (default 1)
        Number of channels in the output images.
    nl : int or tuple (default 4)
        Number of layers. By default, generates 64 x 64 x 64 images.
    max_factor : int (default 8)
        Maximum factor to apply to ngf in the successive layers.
    residual_weight : float, optional (default 0.1)
        Weight of the residual mapping.
    mode : str, optional (default 'nearest')
        Interpolation used for upscaling.
    kernel_size : int or tuple, optional (default 3)
        Size of the convolving kernel.
    layer_normalization : nn.Module, optional (default nn.BatchNorm3d)
        Normalization to apply to the output of the convolution (e.g., batch
        normalization).
    last_layer_normalization : nn.Module, optional (default nn.BatchNorm3d)
        Normalization to apply after the last ResNet block.
    weight_normalization : function, optional (default None)
        Normalization to apply to the weights of the convolution (e.g., spectral
        normalization).
    activation : nn.Module, optional (default nn.ReLU)
        Activation to apply after the convolutions and normalizations.
    last_activation : nn.Module, optional (default nn.Tanh)
        Activation to apply at the very end.
    use_attention : bool, optional (default True)
        If True, add a self-attention block in the network.
    skip_z : bool, optional (default True)
        If True, distributes the latent vector to the residual blocks.
    split_z : bool, optional (default True)
        If True, splits the latent vector between the residual blocks.
    embedding : nn.Module, optional (default None)
        Label embedding.
    ne : int, optional (default 200)
        Size of the dictionary of embeddings.
    nd : int, optional (default 128)
        Size of each embedding vector.
    skip_y : bool, optional (default True)
        If True, distributes the embedding vector to the residual blocks.
    input_y : bool, optional (default True)
        If True, inputs the embedding vector with the latent vector. If `skip_y`
        and `input_y` are both False, then the embedding vector, and the labels,
        are not used.

    References
    ----------
    Brock, A., Donahue, J., Simonyan, K. (2018).
        Large Scale GAN Training for High Fidelity Natural Image Synthesis
        arXiv preprint arXiv:1809.11096v1, https://arxiv.org/abs/1809.11096v1
    """
    def __init__(self,
                 nz=120,
                 ngf=64,
                 nc=1,
                 nl=4,
                 max_factor=16,
                 residual_weight=1.,
                 mode='nearest',
                 kernel_size=3,
                 layer_normalization=nn.BatchNorm3d,
                 last_layer_normalization=nn.BatchNorm3d,
                 weight_normalization=nn.utils.spectral_norm,
                 activation=nn.ReLU,
                 last_activation=nn.Tanh,
                 use_attention=True,
                 skip_z=True,
                 split_z=True,
                 embedding=None,
                 ne=200,
                 nd=128,
                 skip_y=True,
                 input_y=True):

        super(Generator3d, self).__init__(nz, embedding, ne, nd)

        self.skip_z = skip_z
        self.split_z = split_z
        self.skip_y = skip_y
        self.input_y = input_y

        self.nl = _triple(nl)
        if self.skip_z == True and self.split_z == True:
            nz = nz//(max(self.nl) + 1)
        if self.embedding is not None and self.input_y == True and self.split_z == False:
            nz += self.nd
        factor = 2**max(self.nl)
        main = [LinearBlock(nz, ngf*min(factor, max_factor)*4*4*4, bias=False,
                            weight_normalization=weight_normalization, reshape=(-1, 4, 4, 4))]
        for i in range(max(self.nl)):
            new_factor = max(1, factor//2)
            scale_factor = tuple([2 if i < j and j > 0 else 1 for j in self.nl])
            filter = [kernel_size if i < j and j > 0 else 1 for j in self.nl]
            padding = [kernel_size//2 if i < j and j > 0 else 0 for j in self.nl]
            main += [ResBlockUpscale3d(ngf*min(factor, max_factor), ngf*min(new_factor, max_factor),
                                       scale_factor=scale_factor, mode=mode, residual_weight=residual_weight,
                                       kernel_size=filter, padding=padding, layer_normalization=layer_normalization,
                                       weight_normalization=weight_normalization, activation=activation)]
            if i == max(self.nl) - 2 and use_attention == True:
                main += [SelfAttentionBlock3d(ngf*min(new_factor, max_factor), weight_normalization=weight_normalization)]
            factor = new_factor
        if last_layer_normalization is not None:
            main += [last_layer_normalization(ngf)]
        main += [activation()]
        main += [ConvBlock3d(ngf, nc, kernel_size, 1, kernel_size//2, bias=False, layer_normalization=None,
                             weight_normalization=weight_normalization, activation=last_activation)]
        self.main = BlockSequential(*main)

    def forward(self, input):

        use_dict = True
        if isinstance(input, dict) == False:
            input = {'data': input}
            use_dict = False

        z = input['data']
        y = None
        if self.split_z == True:
            z = torch.split(z, z.shape[1]//(max(self.nl) + 1), dim=1)
            y = z[1:]
            z = z[0]
        elif self.skip_z == True:
            y = z

        if self.embedding is not None and 'labels' in input:
            _y = self.embedding(input['labels'])
            if self.input_y == True:
                z = torch.cat([z, _y.view(z.shape[0], -1, *z.shape[2:])], dim=1)
            if self.skip_y == True:
                if self.split_z == True:
                    y = tuple(torch.cat([z_i, _y.view(z_i.shape[0], -1, *z_i.shape[2:])], dim=1) for z_i in y)
                elif self.skip_z == True:
                    y = torch.cat([y, _y.view(y.shape[0], -1, *y.shape[2:])], dim=1)
                else:
                    y = _y

        if use_dict == True:
            output = copy(input)
            output['data'] = self.main(z, y)
        else:
            output = self.main(z, y)

        return output


class Discriminator3d(BaseDiscriminator):
    """
    RESNET projection discriminator for 3D images.
    
    Parameters
    ----------
    ndf : int (default 64)
        Initial number of filters for the convolution.
    nc : int (default 1)
        Number of channels in the output images.
    nl : int or tuple (default 4)
        Number of layers. By default, generates 64 x 64 x 64 images.
    max_factor : int (default 8)
        Maximum factor to apply to ndf in the successive layers.
    residual_weight : float, optional (default 0.1)
        Weight of the residual mapping.
    kernel_size : int or tuple, optional (default 3)
        Size of the convolving kernel.
    layer_normalization : nn.Module, optional (default nn.BatchNorm3d)
        Normalization to apply to the output of the convolution (e.g., batch
        normalization).
    weight_normalization : function, optional (default None)
        Normalization to apply to the weights of the convolution (e.g., spectral
        normalization).
    activation : nn.Module, optional (default nn.LeakyReLU)
        Activation to apply after the convolutions and normalizations.
    use_attention : bool, optional (default True)
        If True, add a self-attention block in the network.
    embedding : nn.Module, optional (default None)
        Label embedding.
    ne : int, optional (default 200)
        Size of the dictionary of embeddings.
    nd : int, optional (default 128)
        Size of each embedding vector.

    References
    ----------
    Brock, A., Donahue, J., Simonyan, K. (2018).
        Large Scale GAN Training for High Fidelity Natural Image Synthesis
        arXiv preprint arXiv:1809.11096v1, https://arxiv.org/abs/1809.11096v1
    """
    def __init__(self,
                 ndf=64,
                 nc=1,
                 nl=4,
                 max_factor=16,
                 residual_weight=1.,
                 kernel_size=3,
                 layer_normalization=None,
                 weight_normalization=nn.utils.spectral_norm,
                 activation=nn.ReLU,
                 use_attention=True,
                 embedding=None,
                 ne=200,
                 nd=1024):

        super(Discriminator3d, self).__init__(embedding, ne, nd)

        nl = _triple(nl)
        factor = 1
        scale_factor = [2 if j > 0 else 1 for j in nl]
        filter = [kernel_size if j > 0 else 1 for j in nl]
        padding = [kernel_size//2 if j > 0 else 0 for j in nl]
        main = [ResBlockDownscale3d(nc, ndf, scale_factor=scale_factor, residual_weight=residual_weight,
                                    kernel_size=filter, padding=padding, layer_normalization=layer_normalization,
                                    weight_normalization=weight_normalization, activation=activation)]
        if use_attention == True:
            main += [SelfAttentionBlock3d(ndf, weight_normalization=weight_normalization)]
        for i in range(1, max(nl)):
            new_factor = min(factor*2, max_factor)
            scale_factor = [2 if i < j and j > 0 else 1 for j in nl]
            filter = [kernel_size if i < j and j > 0 else 1 for j in nl]
            padding = [kernel_size//2 if i < j and j > 0 else 0 for j in nl]
            main += [ResBlockDownscale3d(ndf*factor, ndf*new_factor, scale_factor=scale_factor, residual_weight=residual_weight,
                                         kernel_size=filter, padding=padding, layer_normalization=layer_normalization,
                                         weight_normalization=weight_normalization, activation=activation)]
            factor = new_factor
        filter = [kernel_size if max(nl) == j and j > 0 else 1 for j in nl]
        padding = [kernel_size//2 if max(nl) == j and j > 0 else 0 for j in nl]
        main += [ResBlock3d(ndf*factor, ndf*factor, residual_weight=residual_weight, kernel_size=filter,
                            padding=padding, layer_normalization=layer_normalization,
                            weight_normalization=weight_normalization, activation=activation)]
        main += [activation()]
        self.main = nn.Sequential(*main)

        self.linear = LinearBlock(ndf*factor, 1, weight_normalization=weight_normalization)

    def forward(self, input):

        if isinstance(input, dict) == False:
            input = {'data': input}
        
        # Global sum pooling
        h = torch.sum(self.main(input['data']), axis=(2, 3, 4))
        output = {'data': self.linear(h).squeeze()}
        if self.embedding is not None and 'labels' in input:
            # Projection
            output['data'] += torch.sum(self.embedding(input['labels'])*h, axis=1).squeeze()
            output['labels'] = input['labels']

        return output


class DeepGenerator3d(Generator3d):
    """
    Deep RESNET generator for 3D images.
    
    Parameters
    ----------
    nz : int (default 128)
        Length of the latent vector.
    ngf : int (default 64)
        Initial number of filters for the convolution.
    nc : int (default 1)
        Number of channels in the output images.
    nl : int or tuple (default 4)
        Number of layers. By default, generates 64 x 64 x 64 images.
    max_factor : int (default 8)
        Maximum factor to apply to ngf in the successive layers.
    residual_weight : float, optional (default 0.1)
        Weight of the residual mapping.
    mode : str, optional (default 'nearest')
        Interpolation used for upscaling.
    kernel_size : int or tuple, optional (default 3)
        Size of the convolving kernel.
    layer_normalization : nn.Module (default nn.BatchNorm3d)
        Normalization to apply to the output of the convolution (e.g., batch
        normalization).
    last_layer_normalization : nn.Module (default nn.BatchNorm3d)
        Normalization to apply after the last ResNet block.
    weight_normalization : function (default None)
        Normalization to apply to the weights of the convolution (e.g., spectral
        normalization).
    activation : nn.Module (default nn.ReLU)
        Activation to apply after the convolutions and normalizations.
    last_activation : nn.Module (default nn.Tanh)
        Activation to apply at the very end.
    use_double_conv : bool, optional (default True)
        If True, uses two 3-by-3 convolution layers in the deep residual blocks.
    use_double_resblocks : bool, optional (default True)
        If True, uses a deep residual block for upscaling followed by a regular
        deep residual block.
    use_attention : bool, optional (default True)
        If True, add a self-attention block in the network.
    skip_z : bool, optional (default False)
        If True, distributes the latent vector to the residual blocks.
    split_z : bool, optional (default True)
        If True, splits the latent vector between the residual blocks.
    embedding : nn.Module, optional (default None)
        Label embedding.
    ne : int, optional (default 200)
        Size of the dictionary of embeddings.
    nd : int, optional (default 128)
        Size of each embedding vector.
    skip_y : bool, optional (default True)
        If True, distributes the embedding vector to the residual blocks.
    input_y : bool, optional (default True)
        If True, inputs the embedding vector with the latent vector. If `skip_y`
        and `input_y` are both False, then the embedding vector, and the labels,
        are not used.

    References
    ----------
    Brock, A., Donahue, J., Simonyan, K. (2018).
        Large Scale GAN Training for High Fidelity Natural Image Synthesis
        arXiv preprint arXiv:1809.11096v1, https://arxiv.org/abs/1809.11096v1
    """
    def __init__(self,
                 nz=128,
                 ngf=64,
                 nc=1,
                 nl=4,
                 max_factor=16,
                 residual_weight=1.,
                 mode='nearest',
                 kernel_size=3,
                 layer_normalization=nn.BatchNorm3d,
                 last_layer_normalization=nn.BatchNorm3d,
                 weight_normalization=nn.utils.spectral_norm,
                 activation=nn.ReLU,
                 last_activation=nn.Tanh,
                 use_double_conv=True,
                 use_double_resblocks=True,
                 use_attention=True,
                 skip_z=False,
                 split_z=True,
                 embedding=None,
                 ne=200,
                 nd=128,
                 skip_y=True,
                 input_y=True):

        super(DeepGenerator3d, self).__init__(nz, ngf, nc, nl, max_factor, residual_weight,
                                              mode, kernel_size, layer_normalization,
                                              last_layer_normalization, weight_normalization,
                                              activation, last_activation, use_attention,
                                              skip_z, split_z, embedding, ne, nd,
                                              skip_y, input_y)

        self.nl = _triple(nl)
        if self.skip_z == True and self.split_z == True:
            nz = nz//(max(self.nl) + 1)
        if self.embedding is not None and self.input_y == True and self.split_z == False:
            nz += self.nd
        factor = 2**max(self.nl)
        # main = [LinearBlock(nz, ngf*min(factor, max_factor)*4*4*4, bias=False,
        #                     weight_normalization=weight_normalization, reshape=(-1, 4, 4, 4))]
        filter = [4 if j > 0 else 1 for j in nl]
        main = [ConvBlockTranspose3d(nz, ngf*min(factor, max_factor), filter, 1, 0, bias=False,
                                     weight_normalization=weight_normalization)]
        for i in range(max(self.nl)):
            new_factor = max(1, factor//2)
            scale_factor = tuple([2 if i < j and j > 0 else 1 for j in self.nl])
            filter = [kernel_size if i < j and j > 0 else 1 for j in self.nl]
            padding = [kernel_size//2 if i < j and j > 0 else 0 for j in self.nl]
            main += [DeepResBlockUpscale3d(ngf*min(factor, max_factor), ngf*min(new_factor, max_factor),
                                           scale_factor=scale_factor, mode=mode, residual_weight=residual_weight,
                                           kernel_size=filter, padding=padding, use_double_conv=use_double_conv,
                                           layer_normalization=layer_normalization, weight_normalization=weight_normalization,
                                           activation=activation)]
            if use_double_resblocks == True:
                main += [DeepResBlock3d(ngf*min(new_factor, max_factor), ngf*min(new_factor, max_factor),
                                        residual_weight=residual_weight, kernel_size=filter, padding=padding,
                                        use_double_conv=use_double_conv, layer_normalization=layer_normalization,
                                        weight_normalization=weight_normalization, activation=activation)]
            if i == max(self.nl) - 2 and use_attention == True:
                main += [SelfAttentionBlock3d(ngf*min(new_factor, max_factor), weight_normalization=weight_normalization)]
            factor = new_factor
        if last_layer_normalization is not None:
            main += [last_layer_normalization(ngf)]
        main += [activation()]
        main += [ConvBlock3d(ngf, nc, kernel_size, 1, kernel_size//2, bias=False, layer_normalization=None,
                             weight_normalization=weight_normalization, activation=last_activation)]
        self.main = BlockSequential(*main)


class DeepDiscriminator3d(Discriminator3d):
    """
    Deep RESNET projection discriminator for 3D images.
    
    Parameters
    ----------
    ndf : int (default 64)
        Initial number of filters for the convolution.
    nc : int (default 1)
        Number of channels in the output images.
    nl : int or tuple (default 4)
        Number of layers. By default, generates 64 x 64 x 64 images.
    max_factor : int (default 8)
        Maximum factor to apply to ndf in the successive layers.
    residual_weight : float, optional (default 0.1)
        Weight of the residual mapping.
    kernel_size : int or tuple, optional (default 3)
        Size of the convolving kernel.
    layer_normalization : nn.Module, optional (default nn.BatchNorm3d)
        Normalization to apply to the output of the convolution (e.g., batch
        normalization).
    weight_normalization : function, optional (default None)
        Normalization to apply to the weights of the convolution (e.g., spectral
        normalization).
    activation : nn.Module, optional (default nn.LeakyReLU)
        Activation to apply after the convolutions and normalizations.
    use_double_conv : bool, optional (default True)
        If True, uses two 3-by-3 convolution layers in the deep residual blocks.
    use_double_resblocks : bool, optional (default True)
        If True, uses a deep residual block for downscaling followed by a regular
        deep residual block.
    use_attention : bool, optional (default True)
        If True, add a self-attention block in the network.
    embedding : nn.Module, optional (default None)
        Label embedding.
    ne : int, optional (default 200)
        Size of the dictionary of embeddings.
    nd : int, optional (default 128)
        Size of each embedding vector.

    References
    ----------
    Brock, A., Donahue, J., Simonyan, K. (2018).
        Large Scale GAN Training for High Fidelity Natural Image Synthesis
        arXiv preprint arXiv:1809.11096v1, https://arxiv.org/abs/1809.11096v1
    """
    def __init__(self,
                 ndf=64,
                 nc=1,
                 nl=4,
                 max_factor=16,
                 residual_weight=1.,
                 kernel_size=3,
                 layer_normalization=None,
                 weight_normalization=nn.utils.spectral_norm,
                 activation=nn.ReLU,
                 use_double_conv=True,
                 use_double_resblocks=True,
                 use_attention=True,
                 embedding=None,
                 ne=200,
                 nd=1024):

        super(DeepDiscriminator3d, self).__init__(ndf, nc, nl, max_factor, residual_weight,
                                                  kernel_size, layer_normalization,
                                                  weight_normalization, activation,
                                                  use_attention, embedding, ne, nd)

        nl = _triple(nl)
        factor = 1
        scale_factor = [2 if j > 0 else 1 for j in nl]
        filter = [kernel_size if j > 0 else 1 for j in nl]
        padding = [kernel_size//2 if j > 0 else 0 for j in nl]
        main = [ConvBlock3d(nc, ndf, kernel_size, 1, kernel_size//2, bias=False, layer_normalization=None, weight_normalization=weight_normalization)]
        for i in range(0, max(nl)):
            new_factor = min(factor*2, max_factor)
            scale_factor = [2 if i < j and j > 0 else 1 for j in nl]
            filter = [kernel_size if i < j and j > 0 else 1 for j in nl]
            padding = [kernel_size//2 if i < j and j > 0 else 0 for j in nl]
            main += [DeepResBlockDownscale3d(ndf*factor, ndf*new_factor, scale_factor=scale_factor, residual_weight=residual_weight,
                                             kernel_size=filter, padding=padding, use_double_conv=use_double_conv,
                                             layer_normalization=layer_normalization, weight_normalization=weight_normalization,
                                             activation=activation)]
            if use_double_resblocks == True:
                main += [DeepResBlock3d(ndf*new_factor, ndf*new_factor, residual_weight=residual_weight, kernel_size=filter, padding=padding,
                                        use_double_conv=use_double_conv, layer_normalization=layer_normalization,
                                        weight_normalization=weight_normalization, activation=activation)]
            if i == 0 and use_attention == True:
                main += [SelfAttentionBlock3d(ndf*new_factor, weight_normalization=weight_normalization)]
            factor = new_factor
        main += [activation()]
        self.main = nn.Sequential(*main)

        self.linear = LinearBlock(ndf*factor, 1, weight_normalization=weight_normalization)


class DeepAuxiliaryDiscriminator3d(Discriminator3d):
    """
    Deep RESNET discriminator for 3D images with an auxiliary network for 
    conditioning.
    
    Parameters
    ----------
    ndf : int (default 64)
        Initial number of filters for the convolution.
    nc : int (default 1)
        Number of channels in the output images.
    nl : int or tuple (default 4)
        Number of layers. By default, generates 64 x 64 x 64 images.
    max_factor : int (default 8)
        Maximum factor to apply to ndf in the successive layers.
    residual_weight : float, optional (default 0.1)
        Weight of the residual mapping.
    kernel_size : int or tuple, optional (default 3)
        Size of the convolving kernel.
    layer_normalization : nn.Module, optional (default nn.BatchNorm3d)
        Normalization to apply to the output of the convolution (e.g., batch
        normalization).
    weight_normalization : function, optional (default None)
        Normalization to apply to the weights of the convolution (e.g., spectral
        normalization).
    activation : nn.Module, optional (default nn.LeakyReLU)
        Activation to apply after the convolutions and normalizations.
    use_double_conv : bool, optional (default True)
        If True, uses two 3-by-3 convolution layers in the deep residual blocks.
    use_double_resblocks : bool, optional (default True)
        If True, uses a deep residual block for downscaling followed by a regular
        deep residual block.
    use_attention : bool, optional (default True)
        If True, add a self-attention block in the network.
    embedding : nn.Module, optional (default None)
        Label embedding.
    ne : int, optional (default 200)
        Size of the dictionary of embeddings.
    nd : int, optional (default 128)
        Size of each embedding vector.

    References
    ----------
    Brock, A., Donahue, J., Simonyan, K. (2018).
        Large Scale GAN Training for High Fidelity Natural Image Synthesis
        arXiv preprint arXiv:1809.11096v1, https://arxiv.org/abs/1809.11096v1
    Chen, X., Duan, Y., Houthooft, R., Schulman, J., Sutskever, I., & Abbeel, P. (2016).
        Infogan: Interpretable representation learning by information maximizing generative adversarial nets
        Advances in neural information processing systems, 29
    Odena, A., Olah, C., & Shlens, J. (2017).
        Conditional image synthesis with auxiliary classifier gans
        In International conference on machine learning (pp. 2642-2651). PMLR
    """
    def __init__(self,
                 ndf=64,
                 nc=1,
                 nl=4,
                 max_factor=16,
                 residual_weight=1.,
                 kernel_size=3,
                 layer_normalization=None,
                 weight_normalization=nn.utils.spectral_norm,
                 activation=nn.ReLU,
                 use_double_conv=True,
                 use_double_resblocks=True,
                 use_attention=True,
                 embedding=None,
                 ne=200,
                 nd=1024):

        super(DeepAuxiliaryDiscriminator3d, self).__init__(ndf, nc, nl, max_factor, residual_weight,
                                                           kernel_size, layer_normalization,
                                                           weight_normalization, activation,
                                                           use_attention, embedding, ne, nd)

        nl = _triple(nl)
        factor = 1
        scale_factor = [2 if j > 0 else 1 for j in nl]
        filter = [kernel_size if j > 0 else 1 for j in nl]
        padding = [kernel_size//2 if j > 0 else 0 for j in nl]
        main = [ConvBlock3d(nc, ndf, kernel_size, 1, kernel_size//2, bias=False, layer_normalization=None, weight_normalization=weight_normalization)]
        for i in range(0, max(nl)):
            new_factor = min(factor*2, max_factor)
            scale_factor = [2 if i < j and j > 0 else 1 for j in nl]
            filter = [kernel_size if i < j and j > 0 else 1 for j in nl]
            padding = [kernel_size//2 if i < j and j > 0 else 0 for j in nl]
            main += [DeepResBlockDownscale3d(ndf*factor, ndf*new_factor, scale_factor=scale_factor, residual_weight=residual_weight,
                                             kernel_size=filter, padding=padding, use_double_conv=use_double_conv,
                                             layer_normalization=layer_normalization, weight_normalization=weight_normalization,
                                             activation=activation)]
            if use_double_resblocks == True:
                main += [DeepResBlock3d(ndf*new_factor, ndf*new_factor, residual_weight=residual_weight, kernel_size=filter, padding=padding,
                                        use_double_conv=use_double_conv, layer_normalization=layer_normalization,
                                        weight_normalization=weight_normalization, activation=activation)]
            if i == 0 and use_attention == True:
                main += [SelfAttentionBlock3d(ndf*new_factor, weight_normalization=weight_normalization)]
            factor = new_factor
        main += [activation()]
        filter = [4 if j > 0 else 1 for j in nl]
        main += [ConvBlock3d(ndf*factor, self.ne, filter, 1, 0, bias=False, layer_normalization=None, weight_normalization=weight_normalization, activation=None)]
        self.main = nn.Sequential(*main)

        self.linear = LinearBlock(self.ne, 1)

    def forward(self, input):

        if isinstance(input, dict) == False:
            input = {'data': input}
        
        output = {'data': self.main(input['data'])}
        if self.embedding is not None:
            output['labels'] = self.embedding(output['data'])
        output['data'] = self.linear(output['data']).squeeze()

        return output
    