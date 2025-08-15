"""Building blocks for convolutional neural networks"""

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

import torch
import torch.nn as nn
from torch.nn.modules.utils import _pair, _triple
from torch.nn.modules.batchnorm import _BatchNorm

from .utils import _ConditionalBatchNorm


################################################################################
# nD

class BlockSequential(nn.Sequential):
    """
    Sequential container that can handle different inputs for different layers.
    """
    def forward(self, input, label=None):

        cond_modules = (
            _ConditionalBatchNorm,
            ConvBlock2d, ConvBlock3d,
            ConvBlockTranspose2d, ConvBlockTranspose3d,
            ResBlock2d, ResBlock3d, DeepResBlock3d,
            ResBlockUpscale2d, ResBlockUpscale3d, DeepResBlockUpscale3d,
            ResBlockDownscale2d, ResBlockDownscale3d, DeepResBlockDownscale3d,
        )
        for i, module in enumerate(self):
            if isinstance(module, cond_modules) == True:
                input = module(input, label[i] if isinstance(label, (tuple, list)) else label)
            else:
                input = module(input)

        return input


class ConstantBlock(nn.Module):
    """
    Block for a constant parameter.
    """
    def __init__(self, in_channels, size=4):

        super(ConstantBlock, self).__init__()
        
        size = (size,) if isinstance(size, int) else size
        self.constant = nn.Parameter(torch.randn(1, in_channels, *size))

    def forward(self, input, latent_shape=None):
        
        batch_size = input.shape[0]
        if latent_shape is None:
            latent_shape = (1,)*(input.ndim - 1)
        output = self.constant.repeat(batch_size, *latent_shape)

        return output


class LinearBlock(nn.Module):
    """
    Block of operations to perform a linear transformation, normalization, and
    activation.
    
    Parameters
    ----------
    in_features : int
        Number of features in the input vector.
    out_features : int
        Number of features produced by the transformation.
    bias : bool, optional (default True)
        If True, adds a learnable bias to the output.
    layer_normalization : nn.Module, optional (default None)
        Normalization to apply to the output of the transformation (e.g., batch
        normalization).
    weight_normalization : function or array-like of shape (n_norms,), optional (default None)
        Normalization(s) to apply to the weights of the transformation (e.g.,
        spectral normalization).
    activation : nn.Module, optional (default None)
        Activation to apply to the output of the normalization, if any, and the
        transformation otherwise.
    """
    def __init__(self,
                 in_features,
                 out_features,
                 bias=True,
                 layer_normalization=None,
                 weight_normalization=None,
                 activation=None,
                 reshape=None):

        super(LinearBlock, self).__init__()

        if isinstance(layer_normalization, _BatchNorm):
            bias = False
        if (weight_normalization is not None and
            isinstance(weight_normalization, (tuple, list)) == False):
            weight_normalization = [weight_normalization]

        self.reshape = reshape

        self.main = [nn.Linear(in_features,
                               out_features,
                               bias=bias)]
        if weight_normalization is not None:
            for norm in weight_normalization:
                self.main[0] = norm(self.main[0])
        if layer_normalization is not None:
            self.main += [layer_normalization(out_features)]
        if activation is not None:
            self.main += [activation()]
        self.main = nn.Sequential(*self.main)

    def forward(self, input):

        output = self.main(input.flatten(1))
        if self.reshape is not None:
            output = output.view(output.shape[0], *self.reshape)

        return output


class EmbeddingBlock(nn.Module):
    """
    Block of operations to perform a linear transformation, normalization, and
    activation.
    
    Parameters
    ----------
    num_embeddings : int
        Size of the dictionary of embeddings.
    embedding_dim : int
        Size of each embedding vector.
    padding_idx : int, optional (default None)
        If specified, the entries at `padding_idx` do not contribute to the
        gradient; therefore, the embedding vector at `padding_idx` is not updated
        during training, i.e. it remains as a fixed "pad". For a newly constructed
        Embedding, the embedding vector at `padding_idx` will default to all zeros,
        but can be updated to another value to be used as the padding vector.
    max_norm : float, optional (default None)
        If given, each embedding vector with norm larger than `max_norm` is
        renormalized to have norm `max_norm`.
    norm_type : float, optional (default 2.)
        The p of the p-norm to compute for the `max_norm` option.
    scale_grad_by_freq : bool, optional (default False)
        If given, this will scale gradients by the inverse of frequency of the
        words in the mini-batch. 
    sparse : bool, optional (default False)
         If True, gradient w.r.t. weight matrix will be a sparse tensor.
    weight_normalization : function or array-like of shape (n_norms,), optional (default None)
        Normalization(s) to apply to the weights of the transformation (e.g.,
        spectral normalization).
    """
    def __init__(self,
                 num_embeddings,
                 embedding_dim,
                 padding_idx=None,
                 max_norm=None,
                 norm_type=2.,
                 scale_grad_by_freq=False,
                 sparse=False,
                 weight_normalization=None):

        super(EmbeddingBlock, self).__init__()

        if (weight_normalization is not None and
            isinstance(weight_normalization, (tuple, list)) == False):
            weight_normalization = [weight_normalization]

        self.main = [nn.Embedding(num_embeddings,
                                  embedding_dim,
                                  padding_idx=padding_idx,
                                  max_norm=max_norm,
                                  norm_type=norm_type,
                                  scale_grad_by_freq=scale_grad_by_freq,
                                  sparse=sparse)]
        if weight_normalization is not None:
            for norm in weight_normalization:
                self.main[0] = norm(self.main[0])
        self.main = nn.Sequential(*self.main)

    def forward(self, input):

        output = self.main(input)

        return output


################################################################################
# Convolution

class _ConvBlock(nn.Module):
    """
    Block of operations to perform a convolution, normalization, and activation.
    
    Parameters
    ----------
    conv : nn.Module
        Convolution to apply.
    in_channels : int
        Number of channels in the input image.
    out_channels : int
        Number of channels produced by the convolution.
    kernel_size : int or tuple
        Size of the convolving kernel.
    stride : int or tuple, optional (default 1)
        Stride of the convolution.
    padding : int or tuple, optional (default 0)
        Zero-padding added to all three sides of the input.
    dilation : int or tuple, optional (default 1)
        Spacing between kernel elements.
    groups : float, optional (default 1)
        Number of blocked connections from input channels to output channels.
    bias : bool, optional (default True)
        If True, adds a learnable bias to the output.
    padding_mode : str, optional (default 'zeros')
        Padding mode.
    layer_normalization : nn.Module, optional (default None)
        Normalization to apply to the output of the convolution (e.g., batch
        normalization).
    weight_normalization : function or array-like of shape (n_norms,), optional (default None)
        Normalization(s) to apply to the weights of the transformation (e.g.,
        spectral normalization).
    activation : nn.Module, optional (default None)
        Activation to apply to the output of the normalization, if any, and the
        convolution otherwise.
    """
    def __init__(self,
                 conv,
                 in_channels,
                 out_channels,
                 kernel_size,
                 stride=1,
                 padding=0,
                 dilation=1,
                 groups=1,
                 bias=True,
                 padding_mode='zeros',
                 layer_normalization=None,
                 weight_normalization=None,
                 activation=None):

        super(_ConvBlock, self).__init__()

        if isinstance(layer_normalization, _BatchNorm):
            bias = False
        if (weight_normalization is not None and
            isinstance(weight_normalization, (tuple, list)) == False):
            weight_normalization = [weight_normalization]

        self.main = [conv(in_channels,
                          out_channels,
                          kernel_size,
                          stride=stride,
                          padding=padding,
                          dilation=dilation,
                          groups=groups,
                          bias=bias,
                          padding_mode=padding_mode)]
        if weight_normalization is not None:
            for norm in weight_normalization:
                self.main[0] = norm(self.main[0])
        if layer_normalization is not None:
            self.main += [layer_normalization(out_channels)]
        if activation is not None:
            self.main += [activation()]
        self.main = BlockSequential(*self.main)

    def forward(self, input, label=None):

        output = self.main(input, label)

        return output


class ConvBlock2d(_ConvBlock):
    """
    Block of operations to perform a convolution, normalization, and activation.
    
    Parameters
    ----------
    in_channels : int
        Number of channels in the input image.
    out_channels : int
        Number of channels produced by the convolution.
    kernel_size : int or tuple
        Size of the convolving kernel.
    stride : int or tuple, optional (default 1)
        Stride of the convolution.
    padding : int or tuple, optional (default 0)
        Zero-padding added to all three sides of the input.
    dilation : int or tuple, optional (default 1)
        Spacing between kernel elements.
    groups : float, optional (default 1)
        Number of blocked connections from input channels to output channels.
    bias : bool, optional (default True)
        If True, adds a learnable bias to the output.
    padding_mode : str, optional (default 'zeros')
        Padding mode.
    layer_normalization : nn.Module, optional (default None)
        Normalization to apply to the output of the convolution (e.g., batch
        normalization).
    weight_normalization : function or array-like of shape (n_norms,), optional (default None)
        Normalization(s) to apply to the weights of the transformation (e.g.,
        spectral normalization).
    activation : nn.Module, optional (default None)
        Activation to apply to the output of the normalization, if any, and the
        convolution otherwise.
    """
    def __init__(self,
                 in_channels,
                 out_channels,
                 kernel_size,
                 stride=1,
                 padding=0,
                 dilation=1,
                 groups=1,
                 bias=True,
                 padding_mode='zeros',
                 layer_normalization=None,
                 weight_normalization=None,
                 activation=None):

        super(ConvBlock2d, self).__init__(nn.Conv2d,
                                          in_channels,
                                          out_channels,
                                          kernel_size,
                                          stride=stride,
                                          padding=padding,
                                          dilation=dilation,
                                          groups=groups,
                                          bias=bias,
                                          padding_mode=padding_mode,
                                          layer_normalization=layer_normalization,
                                          weight_normalization=weight_normalization,
                                          activation=activation)


class ConvBlock3d(_ConvBlock):
    """
    Block of operations to perform a convolution, normalization, and activation.
    
    Parameters
    ----------
    in_channels : int
        Number of channels in the input image.
    out_channels : int
        Number of channels produced by the convolution.
    kernel_size : int or tuple
        Size of the convolving kernel.
    stride : int or tuple, optional (default 1)
        Stride of the convolution.
    padding : int or tuple, optional (default 0)
        Zero-padding added to all three sides of the input.
    dilation : int or tuple, optional (default 1)
        Spacing between kernel elements.
    groups : float, optional (default 1)
        Number of blocked connections from input channels to output channels.
    bias : bool, optional (default True)
        If True, adds a learnable bias to the output.
    padding_mode : str, optional (default 'zeros')
        Padding mode.
    layer_normalization : nn.Module, optional (default None)
        Normalization to apply to the output of the convolution (e.g., batch
        normalization).
    weight_normalization : function or array-like of shape (n_norms,), optional (default None)
        Normalization(s) to apply to the weights of the transformation (e.g.,
        spectral normalization).
    activation : nn.Module, optional (default None)
        Activation to apply to the output of the normalization, if any, and the
        convolution otherwise.
    """
    def __init__(self,
                 in_channels,
                 out_channels,
                 kernel_size,
                 stride=1,
                 padding=0,
                 dilation=1,
                 groups=1,
                 bias=True,
                 padding_mode='zeros',
                 layer_normalization=None,
                 weight_normalization=None,
                 activation=None):

        super(ConvBlock3d, self).__init__(nn.Conv3d,
                                          in_channels,
                                          out_channels,
                                          kernel_size,
                                          stride=stride,
                                          padding=padding,
                                          dilation=dilation,
                                          groups=groups,
                                          bias=bias,
                                          padding_mode=padding_mode,
                                          layer_normalization=layer_normalization,
                                          weight_normalization=weight_normalization,
                                          activation=activation)


################################################################################
# Transpose convolution

class _ConvBlockTranspose(nn.Module):
    """
    Block of operations to perform a transpose convolution, normalization, and
    activation.
    
    Parameters
    ----------
    conv_transpose : nn.Module
        Transpose convolution to apply.
    in_channels : int
        Number of channels in the input image.
    out_channels : int
        Number of channels produced by the convolution.
    kernel_size : int or tuple
        Size of the convolving kernel.
    stride : int or tuple, optional (default 1)
        Stride of the convolution.
    padding : int or tuple, optional (default 0)
        Zero-padding added to all three sides of the input.
    output_padding : int or tuple, optional (default 0)
        Additional size added to one side of each dimension in the output shape.
    dilation : int or tuple, optional (default 1)
        Spacing between kernel elements.
    groups : float, optional (default 1)
        Number of blocked connections from input channels to output channels.
    bias : bool, optional (default True)
        If True, adds a learnable bias to the output.
    padding_mode : str, optional (default 'zeros')
        Padding mode.
    layer_normalization : nn.Module, optional (default None)
        Normalization to apply to the output of the convolution (e.g., batch
        normalization).
    weight_normalization : function or array-like of shape (n_norms,), optional (default None)
        Normalization(s) to apply to the weights of the transformation (e.g.,
        spectral normalization).
    activation : nn.Module, optional (default None)
        Activation to apply to the output of the normalization, if any, and the
        convolution otherwise.
    """
    def __init__(self,
                 conv_transpose,
                 in_channels,
                 out_channels,
                 kernel_size,
                 stride=1,
                 padding=0,
                 output_padding=0,
                 dilation=1,
                 groups=1,
                 bias=True,
                 padding_mode='zeros',
                 layer_normalization=None,
                 weight_normalization=None,
                 activation=None):

        super(_ConvBlockTranspose, self).__init__()

        if isinstance(layer_normalization, _BatchNorm):
            bias = False
        if (weight_normalization is not None and
            isinstance(weight_normalization, (tuple, list)) == False):
            weight_normalization = [weight_normalization]

        self.main = [conv_transpose(in_channels,
                                    out_channels,
                                    kernel_size,
                                    stride=stride,
                                    padding=padding,
                                    output_padding=output_padding,
                                    dilation=dilation,
                                    groups=groups,
                                    bias=bias,
                                    padding_mode=padding_mode)]
        if weight_normalization is not None:
            for norm in weight_normalization:
                self.main[0] = norm(self.main[0])
        if layer_normalization is not None:
            self.main += [layer_normalization(out_channels)]
        if activation is not None:
            self.main += [activation()]
        self.main = BlockSequential(*self.main)

    def forward(self, input, label=None):

        output = self.main(input, label)

        return output


class ConvBlockTranspose2d(_ConvBlockTranspose):
    """
    Block of operations to perform a transpose convolution, normalization, and
    activation.
    
    Parameters
    ----------
    in_channels : int
        Number of channels in the input image.
    out_channels : int
        Number of channels produced by the convolution.
    kernel_size : int or tuple
        Size of the convolving kernel.
    stride : int or tuple, optional (default 1)
        Stride of the convolution.
    padding : int or tuple, optional (default 0)
        Zero-padding added to all three sides of the input.
    output_padding : int or tuple, optional (default 0)
        Additional size added to one side of each dimension in the output shape.
    dilation : int or tuple, optional (default 1)
        Spacing between kernel elements.
    groups : float, optional (default 1)
        Number of blocked connections from input channels to output channels.
    bias : bool, optional (default True)
        If True, adds a learnable bias to the output.
    padding_mode : str, optional (default 'zeros')
        Padding mode.
    layer_normalization : nn.Module, optional (default None)
        Normalization to apply to the output of the convolution (e.g., batch
        normalization).
    weight_normalization : function or array-like of shape (n_norms,), optional (default None)
        Normalization(s) to apply to the weights of the transformation (e.g.,
        spectral normalization).
    activation : nn.Module, optional (default None)
        Activation to apply to the output of the normalization, if any, and the
        convolution otherwise.
    """
    def __init__(self,
                 in_channels,
                 out_channels,
                 kernel_size,
                 stride=1,
                 padding=0,
                 output_padding=0,
                 dilation=1,
                 groups=1,
                 bias=True,
                 padding_mode='zeros',
                 layer_normalization=None,
                 weight_normalization=None,
                 activation=None):

        super(ConvBlockTranspose2d, self).__init__(nn.ConvTranspose2d,
                                                   in_channels,
                                                   out_channels,
                                                   kernel_size,
                                                   stride=stride,
                                                   padding=padding,
                                                   output_padding=output_padding,
                                                   dilation=dilation,
                                                   groups=groups,
                                                   bias=bias,
                                                   padding_mode=padding_mode,
                                                   layer_normalization=layer_normalization,
                                                   weight_normalization=weight_normalization,
                                                   activation=activation)


class ConvBlockTranspose3d(_ConvBlockTranspose):
    """
    Block of operations to perform a transpose convolution, normalization, and
    activation.
    
    Parameters
    ----------
    in_channels : int
        Number of channels in the input image.
    out_channels : int
        Number of channels produced by the convolution.
    kernel_size : int or tuple
        Size of the convolving kernel.
    stride : int or tuple, optional (default 1)
        Stride of the convolution.
    padding : int or tuple, optional (default 0)
        Zero-padding added to all three sides of the input.
    output_padding : int or tuple, optional (default 0)
        Additional size added to one side of each dimension in the output shape.
    dilation : int or tuple, optional (default 1)
        Spacing between kernel elements.
    groups : float, optional (default 1)
        Number of blocked connections from input channels to output channels.
    bias : bool, optional (default True)
        If True, adds a learnable bias to the output.
    padding_mode : str, optional (default 'zeros')
        Padding mode.
    layer_normalization : nn.Module, optional (default None)
        Normalization to apply to the output of the convolution (e.g., batch
        normalization).
    weight_normalization : function or array-like of shape (n_norms,), optional (default None)
        Normalization(s) to apply to the weights of the transformation (e.g.,
        spectral normalization).
    activation : nn.Module, optional (default None)
        Activation to apply to the output of the normalization, if any, and the
        convolution otherwise.
    """
    def __init__(self,
                 in_channels,
                 out_channels,
                 kernel_size,
                 stride=1,
                 padding=0,
                 output_padding=0,
                 dilation=1,
                 groups=1,
                 bias=True,
                 padding_mode='zeros',
                 layer_normalization=None,
                 weight_normalization=None,
                 activation=None):

        super(ConvBlockTranspose3d, self).__init__(nn.ConvTranspose3d,
                                                   in_channels,
                                                   out_channels,
                                                   kernel_size,
                                                   stride=stride,
                                                   padding=padding,
                                                   output_padding=output_padding,
                                                   dilation=dilation,
                                                   groups=groups,
                                                   bias=bias,
                                                   padding_mode=padding_mode,
                                                   layer_normalization=layer_normalization,
                                                   weight_normalization=weight_normalization,
                                                   activation=activation)


################################################################################
# Residual blocks

class _ResBlock(nn.Module):
    """
    Residual block.
    
    Parameters
    ----------
    conv : nn.Module
        Convolution to apply.
    in_channels : int
        Number of channels in the input image.
    out_channels : int
        Number of channels produced by the convolution.
    residual_weight : float, optional (default 1.)
        Weight applied to the residual mapping before addition.
    kernel_size : int or tuple, optional (default 3)
        Size of the convolving kernel.
    stride : int or tuple, optional (default 1)
        Stride of the convolution.
    padding : int or tuple, optional (default 1)
        Zero-padding added to all three sides of the input.
    hidden_channels : int, optional (default None)
        Number of channels used in the intermediate layers when out_channels is 
        different from out_channels.
    bias : bool, optional (default False)
        If True, adds a learnable bias to the output.
    padding_mode : str, optional (default 'zeros')
        Padding mode.
    layer_normalization : nn.Module, optional (default None)
        Normalization to apply to the output of the convolution (e.g., batch
        normalization).
    weight_normalization : function or array-like of shape (n_norms,), optional (default None)
        Normalization(s) to apply to the weights of the transformation (e.g.,
        spectral normalization).
    activation : nn.Module, optional (default nn.ReLU)
        Activation to apply to the output of the normalization, if any, and the
        convolution otherwise.
    """
    def __init__(self,
                 conv,
                 in_channels,
                 out_channels,
                 residual_weight=1.,
                 kernel_size=3,
                 stride=1,
                 padding=1,
                 bias=False,
                 padding_mode='zeros',
                 layer_normalization=None,
                 weight_normalization=None,
                 activation=partial(nn.ReLU, inplace=True)):

        super(_ResBlock, self).__init__()

        self.residual_weight = residual_weight
        stride = _triple(stride)
        if isinstance(layer_normalization, _BatchNorm):
            bias = False
        if (weight_normalization is not None and
            isinstance(weight_normalization, (tuple, list)) == False):
            weight_normalization = [weight_normalization]

        self.shortcut = None
        if in_channels != out_channels or any(x > 1 for x in stride):
            self.shortcut = conv(in_channels,
                                 out_channels,
                                 1,
                                 stride=stride,
                                 padding=0,
                                 bias=False)
            if weight_normalization is not None:
                for norm in weight_normalization:
                     self.shortcut = norm(self.shortcut)

        conv_1 = conv(in_channels,
                      out_channels,
                      kernel_size,
                      stride=stride,
                      padding=padding,
                      bias=bias,
                      padding_mode=padding_mode)
        conv_2 = conv(out_channels,
                      out_channels,
                      kernel_size,
                      stride=stride,
                      padding=padding,
                      bias=bias,
                      padding_mode=padding_mode)
        if weight_normalization is not None:
            for norm in weight_normalization:
                conv_1 = norm(conv_1)
            for norm in weight_normalization:
                conv_2 = norm(conv_2)

        self.main = []
        if layer_normalization is not None:
            self.main += [layer_normalization(in_channels)]
        self.main += [activation(),
                      conv_1]
        if layer_normalization is not None:
            self.main += [layer_normalization(out_channels)]
        self.main += [activation(),
                      conv_2]
        self.main = BlockSequential(*self.main)

    def forward(self, input, label=None):
        
        output = self.main(input, label)
        residual = input
        if self.shortcut is not None:
            residual = self.shortcut(input)

        return residual + self.residual_weight*output


class ResBlock2d(_ResBlock):
    """
    Residual block.
    
    Parameters
    ----------
    conv : nn.Module
        Convolution to apply.
    in_channels : int
        Number of channels in the input image.
    out_channels : int
        Number of channels produced by the convolution.
    residual_weight : float, optional (default 1.)
        Weight applied to the residual mapping before addition.
    kernel_size : int or tuple, optional (default 3)
        Size of the convolving kernel.
    stride : int or tuple, optional (default 1)
        Stride of the convolution.
    padding : int or tuple, optional (default 1)
        Zero-padding added to all three sides of the input.
    hidden_channels : int, optional (default None)
        Number of channels used in the intermediate layers when out_channels is 
        different from out_channels.
    bias : bool, optional (default False)
        If True, adds a learnable bias to the output.
    padding_mode : str, optional (default 'zeros')
        Padding mode.
    layer_normalization : nn.Module, optional (default BatchNorm2d)
        Normalization to apply to the output of the convolution (e.g., batch
        normalization).
    weight_normalization : function or array-like of shape (n_norms,), optional (default None)
        Normalization(s) to apply to the weights of the transformation (e.g.,
        spectral normalization).
    activation : nn.Module, optional (default nn.ReLU)
        Activation to apply to the output of the normalization, if any, and the
        convolution otherwise.
    """
    def __init__(self,
                 in_channels,
                 out_channels,
                 residual_weight=1.,
                 kernel_size=3,
                 stride=1,
                 padding=1,
                 bias=False,
                 padding_mode='zeros',
                 layer_normalization=nn.BatchNorm2d,
                 weight_normalization=None,
                 activation=partial(nn.ReLU, inplace=True)):

        super(ResBlock2d, self).__init__(nn.Conv2d,
                                         in_channels,
                                         out_channels,
                                         residual_weight=residual_weight,
                                         kernel_size=kernel_size,
                                         stride=stride,
                                         padding=padding,
                                         bias=bias,
                                         padding_mode=padding_mode,
                                         layer_normalization=layer_normalization,
                                         weight_normalization=weight_normalization,
                                         activation=activation)


class ResBlock3d(_ResBlock):
    """
    Residual block.
    
    Parameters
    ----------
    conv : nn.Module
        Convolution to apply.
    in_channels : int
        Number of channels in the input image.
    out_channels : int
        Number of channels produced by the convolution.
    residual_weight : float, optional (default 1.)
        Weight applied to the residual mapping before addition.
    kernel_size : int or tuple, optional (default 3)
        Size of the convolving kernel.
    stride : int or tuple, optional (default 1)
        Stride of the convolution.
    padding : int or tuple, optional (default 1)
        Zero-padding added to all three sides of the input.
    hidden_channels : int, optional (default None)
        Number of channels used in the intermediate layers when out_channels is 
        different from out_channels.
    bias : bool, optional (default False)
        If True, adds a learnable bias to the output.
    padding_mode : str, optional (default 'zeros')
        Padding mode.
    layer_normalization : nn.Module, optional (default BatchNorm3d)
        Normalization to apply to the output of the convolution (e.g., batch
        normalization).
    weight_normalization : function or array-like of shape (n_norms,), optional (default None)
        Normalization(s) to apply to the weights of the transformation (e.g.,
        spectral normalization).
    activation : nn.Module, optional (default nn.ReLU)
        Activation to apply to the output of the normalization, if any, and the
        convolution otherwise.
    """
    def __init__(self,
                 in_channels,
                 out_channels,
                 residual_weight=1.,
                 kernel_size=3,
                 stride=1,
                 padding=1,
                 bias=False,
                 padding_mode='zeros',
                 layer_normalization=nn.BatchNorm3d,
                 weight_normalization=None,
                 activation=partial(nn.ReLU, inplace=True)):

        super(ResBlock3d, self).__init__(nn.Conv3d,
                                         in_channels,
                                         out_channels,
                                         residual_weight=residual_weight,
                                         kernel_size=kernel_size,
                                         stride=stride,
                                         padding=padding,
                                         bias=bias,
                                         padding_mode=padding_mode,
                                         layer_normalization=layer_normalization,
                                         weight_normalization=weight_normalization,
                                         activation=activation)


class _ResBlockUpscale(nn.Module):
    """
    Residual block for upscaling.
    
    Parameters
    ----------
    conv : nn.Module
        Convolution to apply.
    in_channels : int
        Number of channels in the input image.
    out_channels : int
        Number of channels produced by the convolution.
    scale_factor : int or tuple, optional (default 2)
        Scale factor for upscaling.
    mode : str, optional (default 'nearest')
        Interpolation used for upscaling.
    residual_weight : float, optional (default 1.)
        Weight applied to the residual mapping before addition.
    kernel_size : int or tuple, optional (default 3)
        Size of the convolving kernel.
    stride : int or tuple, optional (default 1)
        Stride of the convolution.
    padding : int or tuple, optional (default 1)
        Zero-padding added to all three sides of the input.
    hidden_channels : int, optional (default None)
        Number of channels used in the intermediate layers when out_channels is 
        different from out_channels.
    bias : bool, optional (default False)
        If True, adds a learnable bias to the output.
    padding_mode : str, optional (default 'zeros')
        Padding mode.
    layer_normalization : nn.Module, optional (default None)
        Normalization to apply to the output of the convolution (e.g., batch
        normalization).
    weight_normalization : function or array-like of shape (n_norms,), optional (default None)
        Normalization(s) to apply to the weights of the transformation (e.g.,
        spectral normalization).
    activation : nn.Module, optional (default nn.ReLU)
        Activation to apply to the output of the normalization, if any, and the
        convolution otherwise.
    """
    def __init__(self,
                 conv,
                 in_channels,
                 out_channels,
                 scale_factor=2,
                 mode='nearest',
                 residual_weight=1.,
                 kernel_size=3,
                 stride=1,
                 padding=1,
                 bias=False,
                 padding_mode='zeros',
                 layer_normalization=None,
                 weight_normalization=None,
                 activation=partial(nn.ReLU, inplace=True)):

        super(_ResBlockUpscale, self).__init__()

        if isinstance(layer_normalization, _BatchNorm):
            bias = False
        if (weight_normalization is not None and
            isinstance(weight_normalization, (tuple, list)) == False):
            weight_normalization = [weight_normalization]

        scale_factor = _triple(scale_factor)
        stride = _triple(stride)
        self.residual_weight = residual_weight

        self.shortcut = None
        if in_channels != out_channels or any(x > 1 for x in scale_factor) or any(x > 1 for x in stride):
            self.shortcut = [nn.Upsample(scale_factor=scale_factor,
                                         mode=mode),
                             conv(in_channels,
                                  out_channels,
                                  1,
                                  stride=1,
                                  padding=0,
                                  bias=False)]
            if weight_normalization is not None:
                for norm in weight_normalization:
                     self.shortcut[1] = norm(self.shortcut[1])
            self.shortcut = nn.Sequential(*self.shortcut)

        conv_1 = conv(in_channels,
                      out_channels,
                      kernel_size,
                      stride=stride,
                      padding=padding,
                      bias=bias,
                      padding_mode=padding_mode)
        conv_2 = conv(out_channels,
                      out_channels,
                      kernel_size,
                      stride=stride,
                      padding=padding,
                      bias=bias,
                      padding_mode=padding_mode)
        if weight_normalization is not None:
            for norm in weight_normalization:
                conv_1 = norm(conv_1)
            for norm in weight_normalization:
                conv_2 = norm(conv_2)

        self.main = []
        if layer_normalization is not None:
            self.main += [layer_normalization(in_channels)]
        self.main += [activation(),
                      nn.Upsample(scale_factor=scale_factor,
                                  mode=mode),
                      conv_1]
        if layer_normalization is not None:
            self.main += [layer_normalization(out_channels)]
        self.main += [activation(),
                      conv_2]
        self.main = BlockSequential(*self.main)

    def forward(self, input, label=None):
        
        output = self.main(input, label)
        residual = input
        if self.shortcut is not None:
            residual = self.shortcut(input)

        return residual + self.residual_weight*output


class ResBlockUpscale2d(_ResBlockUpscale):
    """
    Residual block for upscaling.
    
    Parameters
    ----------
    in_channels : int
        Number of channels in the input image.
    out_channels : int
        Number of channels produced by the convolution.
    scale_factor : int or tuple, optional (default 2)
        Scale factor for upscaling.
    mode : str, optional (default 'nearest')
        Interpolation used for upscaling.
    residual_weight : float, optional (default 1.)
        Weight applied to the residual mapping before addition.
    kernel_size : int or tuple, optional (default 3)
        Size of the convolving kernel.
    stride : int or tuple, optional (default 1)
        Stride of the convolution.
    padding : int or tuple, optional (default 1)
        Zero-padding added to all three sides of the input.
    hidden_channels : int, optional (default None)
        Number of channels used in the intermediate layers when out_channels is 
        different from out_channels.
    bias : bool, optional (default False)
        If True, adds a learnable bias to the output.
    padding_mode : str, optional (default 'zeros')
        Padding mode.
    layer_normalization : nn.Module, optional (default BatchNorm2d)
        Normalization to apply to the output of the convolution (e.g., batch
        normalization).
    weight_normalization : function or array-like of shape (n_norms,), optional (default None)
        Normalization(s) to apply to the weights of the transformation (e.g.,
        spectral normalization).
    activation : nn.Module, optional (default nn.ReLU)
        Activation to apply to the output of the normalization, if any, and the
        convolution otherwise.
    """
    def __init__(self,
                 in_channels,
                 out_channels,
                 scale_factor=2,
                 mode='nearest',
                 residual_weight=1.,
                 kernel_size=3,
                 stride=1,
                 padding=1,
                 bias=False,
                 padding_mode='zeros',
                 layer_normalization=nn.BatchNorm2d,
                 weight_normalization=None,
                 activation=partial(nn.ReLU, inplace=True)):

        super(ResBlockUpscale2d, self).__init__(nn.Conv2d,
                                                in_channels,
                                                out_channels,
                                                scale_factor=scale_factor,
                                                mode=mode,
                                                residual_weight=residual_weight,
                                                kernel_size=kernel_size,
                                                stride=stride,
                                                padding=padding,
                                                bias=bias,
                                                padding_mode=padding_mode,
                                                layer_normalization=layer_normalization,
                                                weight_normalization=weight_normalization,
                                                activation=activation)


class ResBlockUpscale3d(_ResBlockUpscale):
    """
    Residual block for upscaling.
    
    Parameters
    ----------
    in_channels : int
        Number of channels in the input image.
    out_channels : int
        Number of channels produced by the convolution.
    scale_factor : int or tuple, optional (default 2)
        Scale factor for upscaling.
    mode : str, optional (default 'nearest')
        Interpolation used for upscaling.
    residual_weight : float, optional (default 1.)
        Weight applied to the residual mapping before addition.
    kernel_size : int or tuple, optional (default 3)
        Size of the convolving kernel.
    stride : int or tuple, optional (default 1)
        Stride of the convolution.
    padding : int or tuple, optional (default 1)
        Zero-padding added to all three sides of the input.
    hidden_channels : int, optional (default None)
        Number of channels used in the intermediate layers when out_channels is 
        different from out_channels.
    bias : bool, optional (default False)
        If True, adds a learnable bias to the output.
    padding_mode : str, optional (default 'zeros')
        Padding mode.
    layer_normalization : nn.Module, optional (default BatchNorm3d)
        Normalization to apply to the output of the convolution (e.g., batch
        normalization).
    weight_normalization : function or array-like of shape (n_norms,), optional (default None)
        Normalization(s) to apply to the weights of the transformation (e.g.,
        spectral normalization).
    activation : nn.Module, optional (default nn.ReLU)
        Activation to apply to the output of the normalization, if any, and the
        convolution otherwise.
    """
    def __init__(self,
                 in_channels,
                 out_channels,
                 scale_factor=2,
                 mode='nearest',
                 residual_weight=1.,
                 kernel_size=3,
                 stride=1,
                 padding=1,
                 bias=False,
                 padding_mode='zeros',
                 layer_normalization=nn.BatchNorm3d,
                 weight_normalization=None,
                 activation=partial(nn.ReLU, inplace=True)):

        super(ResBlockUpscale3d, self).__init__(nn.Conv3d,
                                                in_channels,
                                                out_channels,
                                                scale_factor=scale_factor,
                                                mode=mode,
                                                residual_weight=residual_weight,
                                                kernel_size=kernel_size,
                                                stride=stride,
                                                padding=padding,
                                                bias=bias,
                                                padding_mode=padding_mode,
                                                layer_normalization=layer_normalization,
                                                weight_normalization=weight_normalization,
                                                activation=activation)


class _ResBlockDownscale(nn.Module):
    """
    Residual block for downscaling.
    
    Parameters
    ----------
    conv : nn.Module
        Convolution to apply.
    downscale : nn.Module
        Downscaling layer to apply.
    in_channels : int
        Number of channels in the input image.
    out_channels : int
        Number of channels produced by the convolution.
    scale_factor : int or tuple, optional (default 2)
        Scale factor for downscaling.
    residual_weight : float, optional (default 1.)
        Weight applied to the residual mapping before addition.
    kernel_size : int or tuple, optional (default 3)
        Size of the convolving kernel.
    stride : int or tuple, optional (default 1)
        Stride of the convolution.
    padding : int or tuple, optional (default 1)
        Zero-padding added to all three sides of the input.
    hidden_channels : int, optional (default None)
        Number of channels used in the intermediate layers when out_channels is 
        different from out_channels.
    bias : bool, optional (default False)
        If True, adds a learnable bias to the output.
    padding_mode : str, optional (default 'zeros')
        Padding mode.
    layer_normalization : nn.Module, optional (default None)
        Normalization to apply to the output of the convolution (e.g., batch
        normalization).
    weight_normalization : function or array-like of shape (n_norms,), optional (default None)
        Normalization(s) to apply to the weights of the transformation (e.g.,
        spectral normalization).
    activation : nn.Module, optional (default nn.ReLU)
        Activation to apply to the output of the normalization, if any, and the
        convolution otherwise.
    """
    def __init__(self,
                 conv,
                 downscale,
                 in_channels,
                 out_channels,
                 scale_factor=2,
                 residual_weight=1.,
                 kernel_size=3,
                 stride=1,
                 padding=1,
                 bias=False,
                 padding_mode='zeros',
                 layer_normalization=None,
                 weight_normalization=None,
                 activation=partial(nn.ReLU, inplace=True)):

        super(_ResBlockDownscale, self).__init__()

        if isinstance(layer_normalization, _BatchNorm):
            bias = False
        if (weight_normalization is not None and
            isinstance(weight_normalization, (tuple, list)) == False):
            weight_normalization = [weight_normalization]

        scale_factor = _triple(scale_factor)
        stride = _triple(stride)
        self.residual_weight = residual_weight

        self.shortcut = None
        if in_channels != out_channels or any(x > 1 for x in scale_factor) or any(x > 1 for x in stride):
            self.shortcut = [conv(in_channels,
                                  out_channels,
                                  1,
                                  stride=1,
                                  padding=0,
                                  bias=False),
                             downscale(scale_factor)]
            if weight_normalization is not None:
                for norm in weight_normalization:
                     self.shortcut[0] = norm(self.shortcut[0])
            self.shortcut = nn.Sequential(*self.shortcut)

        conv_1 = conv(in_channels,
                      out_channels,
                      kernel_size,
                      stride=stride,
                      padding=padding,
                      bias=bias,
                      padding_mode=padding_mode)
        conv_2 = conv(out_channels,
                      out_channels,
                      kernel_size,
                      stride=stride,
                      padding=padding,
                      bias=bias,
                      padding_mode=padding_mode)
        if weight_normalization is not None:
            for norm in weight_normalization:
                conv_1 = norm(conv_1)
            for norm in weight_normalization:
                conv_2 = norm(conv_2)

        self.main = []
        if layer_normalization is not None:
            self.main += [layer_normalization(in_channels)]
        self.main += [activation(),
                      conv_1]
        if layer_normalization is not None:
            self.main += [layer_normalization(out_channels)]
        self.main += [activation(),
                      conv_2,
                      downscale(scale_factor)]
        self.main = BlockSequential(*self.main)

    def forward(self, input, label=None):
        
        output = self.main(input, label)
        residual = input
        if self.shortcut is not None:
            residual = self.shortcut(input)

        return residual + self.residual_weight*output


class ResBlockDownscale2d(_ResBlockDownscale):
    """
    Residual block for downscaling.
    
    Parameters
    ----------
    in_channels : int
        Number of channels in the input image.
    out_channels : int
        Number of channels produced by the convolution.
    scale_factor : int or tuple, optional (default 2)
        Scale factor for downscaling.
    residual_weight : float, optional (default 1.)
        Weight applied to the residual mapping before addition.
    kernel_size : int or tuple, optional (default 3)
        Size of the convolving kernel.
    stride : int or tuple, optional (default 1)
        Stride of the convolution.
    padding : int or tuple, optional (default 1)
        Zero-padding added to all three sides of the input.
    hidden_channels : int, optional (default None)
        Number of channels used in the intermediate layers when out_channels is 
        different from out_channels.
    bias : bool, optional (default False)
        If True, adds a learnable bias to the output.
    padding_mode : str, optional (default 'zeros')
        Padding mode.
    layer_normalization : nn.Module, optional (default BatchNorm2d)
        Normalization to apply to the output of the convolution (e.g., batch
        normalization).
    weight_normalization : function or array-like of shape (n_norms,), optional (default None)
        Normalization(s) to apply to the weights of the transformation (e.g.,
        spectral normalization).
    activation : nn.Module, optional (default nn.ReLU)
        Activation to apply to the output of the normalization, if any, and the
        convolution otherwise.
    """
    def __init__(self,
                 in_channels,
                 out_channels,
                 scale_factor=2,
                 residual_weight=1.,
                 kernel_size=3,
                 stride=1,
                 padding=1,
                 bias=False,
                 padding_mode='zeros',
                 layer_normalization=nn.BatchNorm2d,
                 weight_normalization=None,
                 activation=partial(nn.ReLU, inplace=True)):

        super(ResBlockDownscale2d, self).__init__(nn.Conv2d,
                                                  nn.AvgPool2d,
                                                  in_channels,
                                                  out_channels,
                                                  scale_factor=scale_factor,
                                                  residual_weight=residual_weight,
                                                  kernel_size=kernel_size,
                                                  stride=stride,
                                                  padding=padding,
                                                  bias=bias,
                                                  padding_mode=padding_mode,
                                                  layer_normalization=layer_normalization,
                                                  weight_normalization=weight_normalization,
                                                  activation=activation)


class ResBlockDownscale3d(_ResBlockDownscale):
    """
    Residual block for downscaling.
    
    Parameters
    ----------
    in_channels : int
        Number of channels in the input image.
    out_channels : int
        Number of channels produced by the convolution.
    scale_factor : int or tuple, optional (default 2)
        Scale factor for downscaling.
    residual_weight : float, optional (default 1.)
        Weight applied to the residual mapping before addition.
    kernel_size : int or tuple, optional (default 3)
        Size of the convolving kernel.
    stride : int or tuple, optional (default 1)
        Stride of the convolution.
    padding : int or tuple, optional (default 1)
        Zero-padding added to all three sides of the input.
    hidden_channels : int, optional (default None)
        Number of channels used in the intermediate layers when out_channels is 
        different from out_channels.
    bias : bool, optional (default False)
        If True, adds a learnable bias to the output.
    padding_mode : str, optional (default 'zeros')
        Padding mode.
    layer_normalization : nn.Module, optional (default BatchNorm3d)
        Normalization to apply to the output of the convolution (e.g., batch
        normalization).
    weight_normalization : function or array-like of shape (n_norms,), optional (default None)
        Normalization(s) to apply to the weights of the transformation (e.g.,
        spectral normalization).
    activation : nn.Module, optional (default nn.ReLU)
        Activation to apply to the output of the normalization, if any, and the
        convolution otherwise.
    """
    def __init__(self,
                 in_channels,
                 out_channels,
                 scale_factor=2,
                 residual_weight=1.,
                 kernel_size=3,
                 stride=1,
                 padding=1,
                 bias=False,
                 padding_mode='zeros',
                 layer_normalization=nn.BatchNorm3d,
                 weight_normalization=None,
                 activation=partial(nn.ReLU, inplace=True)):

        super(ResBlockDownscale3d, self).__init__(nn.Conv3d,
                                                  nn.AvgPool3d,
                                                  in_channels,
                                                  out_channels,
                                                  scale_factor=scale_factor,
                                                  residual_weight=residual_weight,
                                                  kernel_size=kernel_size,
                                                  stride=stride,
                                                  padding=padding,
                                                  bias=bias,
                                                  padding_mode=padding_mode,
                                                  layer_normalization=layer_normalization,
                                                  weight_normalization=weight_normalization,
                                                  activation=activation)


class _DeepResBlock(nn.Module):
    """
    Deep residual block.
    
    Parameters
    ----------
    conv : nn.Module
        Convolution to apply.
    in_channels : int
        Number of channels in the input image.
    out_channels : int
        Number of channels produced by the convolution.
    channel_factor : int, optional (default 4)
        Factor by which to decrease the number of channels in the two middle
        convolution layers.
    residual_weight : float, optional (default 1.)
        Weight applied to the residual mapping before addition.
    kernel_size : int or tuple, optional (default 3)
        Size of the convolving kernel.
    stride : int or tuple, optional (default 1)
        Stride of the convolution.
    padding : int or tuple, optional (default 1)
        Zero-padding added to all three sides of the input.
    hidden_channels : int, optional (default None)
        Number of channels used in the intermediate layers when out_channels is 
        different from out_channels.
    bias : bool, optional (default False)
        If True, adds a learnable bias to the output.
    padding_mode : str, optional (default 'zeros')
        Padding mode.
    use_double_conv : bool, optional (default True)
        If True, uses two 3-by-3 convolution layers.
    layer_normalization : nn.Module, optional (default None)
        Normalization to apply to the output of the convolution (e.g., batch
        normalization).
    weight_normalization : function or array-like of shape (n_norms,), optional (default None)
        Normalization(s) to apply to the weights of the transformation (e.g.,
        spectral normalization).
    activation : nn.Module, optional (default nn.ReLU)
        Activation to apply to the output of the normalization, if any, and the
        convolution otherwise.
    """
    def __init__(self,
                 conv,
                 in_channels,
                 out_channels,
                 channel_factor=4,
                 residual_weight=1.,
                 kernel_size=3,
                 stride=1,
                 padding=1,
                 bias=False,
                 padding_mode='zeros',
                 use_double_conv=True,
                 layer_normalization=None,
                 weight_normalization=None,
                 activation=partial(nn.ReLU, inplace=True)):

        super(_DeepResBlock, self).__init__()

        if isinstance(layer_normalization, _BatchNorm):
            bias = False
        if (weight_normalization is not None and
            isinstance(weight_normalization, (tuple, list)) == False):
            weight_normalization = [weight_normalization]

        self.residual_weight = residual_weight

        mid_channels = max(in_channels//channel_factor, 1)
        conv_1 = conv(in_channels,
                      mid_channels,
                      1,
                      stride=1,
                      padding=0,
                      bias=bias)
        conv_2 = conv(mid_channels,
                      mid_channels,
                      kernel_size,
                      stride=stride,
                      padding=padding,
                      bias=bias,
                      padding_mode=padding_mode)
        if use_double_conv == True:
            conv_3 = conv(mid_channels,
                          mid_channels,
                          kernel_size,
                          stride=stride,
                          padding=padding,
                          bias=bias,
                          padding_mode=padding_mode)
        conv_4 = conv(mid_channels,
                      out_channels,
                      1,
                      stride=1,
                      padding=0,
                      bias=bias)
        if weight_normalization is not None:
            for norm in weight_normalization:
                conv_1 = norm(conv_1)
            for norm in weight_normalization:
                conv_2 = norm(conv_2)
            if use_double_conv == True:
                for norm in weight_normalization:
                    conv_3 = norm(conv_3)
            for norm in weight_normalization:
                conv_4 = norm(conv_4)

        self.main = []
        if layer_normalization is not None:
            self.main += [layer_normalization(in_channels)]
        self.main += [activation(),
                      conv_1]
        if layer_normalization is not None:
            self.main += [layer_normalization(mid_channels)]
        self.main += [activation(),
                      conv_2]
        if use_double_conv == True:
            if layer_normalization is not None:
                self.main += [layer_normalization(mid_channels)]
            self.main += [activation(),
                        conv_3]
        if layer_normalization is not None:
            self.main += [layer_normalization(mid_channels)]
        self.main += [activation(),
                      conv_4]
        self.main = BlockSequential(*self.main)

    def forward(self, input, label=None):
        
        output = self.main(input, label)

        return input + self.residual_weight*output


class DeepResBlock2d(_DeepResBlock):
    """
    Deep residual block.
    
    Parameters
    ----------
    conv : nn.Module
        Convolution to apply.
    in_channels : int
        Number of channels in the input image.
    out_channels : int
        Number of channels produced by the convolution.
    channel_factor : int, optional (default 4)
        Factor by which to decrease the number of channels in the two middle
        convolution layers.
    residual_weight : float, optional (default 1.)
        Weight applied to the residual mapping before addition.
    kernel_size : int or tuple, optional (default 3)
        Size of the convolving kernel.
    stride : int or tuple, optional (default 1)
        Stride of the convolution.
    padding : int or tuple, optional (default 1)
        Zero-padding added to all three sides of the input.
    hidden_channels : int, optional (default None)
        Number of channels used in the intermediate layers when out_channels is 
        different from out_channels.
    bias : bool, optional (default False)
        If True, adds a learnable bias to the output.
    padding_mode : str, optional (default 'zeros')
        Padding mode.
    use_double_conv : bool, optional (default True)
        If True, uses two 3-by-3 convolution layers.
    layer_normalization : nn.Module, optional (default BatchNorm2d)
        Normalization to apply to the output of the convolution (e.g., batch
        normalization).
    weight_normalization : function or array-like of shape (n_norms,), optional (default None)
        Normalization(s) to apply to the weights of the transformation (e.g.,
        spectral normalization).
    activation : nn.Module, optional (default nn.ReLU)
        Activation to apply to the output of the normalization, if any, and the
        convolution otherwise.
    """
    def __init__(self,
                 in_channels,
                 out_channels,
                 channel_factor=4,
                 residual_weight=1.,
                 kernel_size=3,
                 stride=1,
                 padding=1,
                 bias=False,
                 padding_mode='zeros',
                 use_double_conv=True,
                 layer_normalization=nn.BatchNorm2d,
                 weight_normalization=None,
                 activation=partial(nn.ReLU, inplace=True)):

        super(DeepResBlock2d, self).__init__(nn.Conv2d,
                                             in_channels,
                                             out_channels,
                                             channel_factor=channel_factor,
                                             residual_weight=residual_weight,
                                             kernel_size=kernel_size,
                                             stride=stride,
                                             padding=padding,
                                             bias=bias,
                                             padding_mode=padding_mode,
                                             use_double_conv=use_double_conv,
                                             layer_normalization=layer_normalization,
                                             weight_normalization=weight_normalization,
                                             activation=activation)


class DeepResBlock3d(_DeepResBlock):
    """
    Deep residual block.
    
    Parameters
    ----------
    conv : nn.Module
        Convolution to apply.
    in_channels : int
        Number of channels in the input image.
    out_channels : int
        Number of channels produced by the convolution.
    channel_factor : int, optional (default 4)
        Factor by which to decrease the number of channels in the two middle
        convolution layers.
    residual_weight : float, optional (default 1.)
        Weight applied to the residual mapping before addition.
    kernel_size : int or tuple, optional (default 3)
        Size of the convolving kernel.
    stride : int or tuple, optional (default 1)
        Stride of the convolution.
    padding : int or tuple, optional (default 1)
        Zero-padding added to all three sides of the input.
    hidden_channels : int, optional (default None)
        Number of channels used in the intermediate layers when out_channels is 
        different from out_channels.
    bias : bool, optional (default False)
        If True, adds a learnable bias to the output.
    padding_mode : str, optional (default 'zeros')
        Padding mode.
    use_double_conv : bool, optional (default True)
        If True, uses two 3-by-3 convolution layers.
    layer_normalization : nn.Module, optional (default BatchNorm3d)
        Normalization to apply to the output of the convolution (e.g., batch
        normalization).
    weight_normalization : function or array-like of shape (n_norms,), optional (default None)
        Normalization(s) to apply to the weights of the transformation (e.g.,
        spectral normalization).
    activation : nn.Module, optional (default nn.ReLU)
        Activation to apply to the output of the normalization, if any, and the
        convolution otherwise.
    """
    def __init__(self,
                 in_channels,
                 out_channels,
                 channel_factor=4,
                 residual_weight=1.,
                 kernel_size=3,
                 stride=1,
                 padding=1,
                 bias=False,
                 padding_mode='zeros',
                 use_double_conv=True,
                 layer_normalization=nn.BatchNorm3d,
                 weight_normalization=None,
                 activation=partial(nn.ReLU, inplace=True)):

        super(DeepResBlock3d, self).__init__(nn.Conv3d,
                                             in_channels,
                                             out_channels,
                                             channel_factor=channel_factor,
                                             residual_weight=residual_weight,
                                             kernel_size=kernel_size,
                                             stride=stride,
                                             padding=padding,
                                             bias=bias,
                                             padding_mode=padding_mode,
                                             use_double_conv=use_double_conv,
                                             layer_normalization=layer_normalization,
                                             weight_normalization=weight_normalization,
                                             activation=activation)


class _DeepResBlockUpscale(nn.Module):
    """
    Deep residual block for upscaling.
    
    Parameters
    ----------
    conv : nn.Module
        Convolution to apply.
    in_channels : int
        Number of channels in the input image.
    out_channels : int
        Number of channels produced by the convolution.
    channel_factor : int, optional (default 4)
        Factor by which to decrease the number of channels in the two middle
        convolution layers.
    scale_factor : int or tuple, optional (default 2)
        Scale factor for upscaling.
    mode : str, optional (default 'nearest')
        Interpolation used for upscaling.
    residual_weight : float, optional (default 1.)
        Weight applied to the residual mapping before addition.
    kernel_size : int or tuple, optional (default 3)
        Size of the convolving kernel.
    stride : int or tuple, optional (default 1)
        Stride of the convolution.
    padding : int or tuple, optional (default 1)
        Zero-padding added to all three sides of the input.
    hidden_channels : int, optional (default None)
        Number of channels used in the intermediate layers when out_channels is 
        different from out_channels.
    bias : bool, optional (default False)
        If True, adds a learnable bias to the output.
    padding_mode : str, optional (default 'zeros')
        Padding mode.
    use_double_conv : bool, optional (default True)
        If True, uses two 3-by-3 convolution layers.
    layer_normalization : nn.Module, optional (default None)
        Normalization to apply to the output of the convolution (e.g., batch
        normalization).
    weight_normalization : function or array-like of shape (n_norms,), optional (default None)
        Normalization(s) to apply to the weights of the transformation (e.g.,
        spectral normalization).
    activation : nn.Module, optional (default nn.ReLU)
        Activation to apply to the output of the normalization, if any, and the
        convolution otherwise.
    """
    def __init__(self,
                 conv,
                 in_channels,
                 out_channels,
                 channel_factor=4,
                 scale_factor=2,
                 mode='nearest',
                 residual_weight=1.,
                 kernel_size=3,
                 stride=1,
                 padding=1,
                 bias=False,
                 padding_mode='zeros',
                 use_double_conv=True,
                 layer_normalization=None,
                 weight_normalization=None,
                 activation=partial(nn.ReLU, inplace=True)):

        super(_DeepResBlockUpscale, self).__init__()

        if isinstance(layer_normalization, _BatchNorm):
            bias = False
        if (weight_normalization is not None and
            isinstance(weight_normalization, (tuple, list)) == False):
            weight_normalization = [weight_normalization]

        scale_factor = _triple(scale_factor)
        stride = _triple(stride)
        self.residual_weight = residual_weight

        self.shortcut = None
        if any(x > 1 for x in scale_factor) or any(x > 1 for x in stride):
            self.shortcut = nn.Upsample(scale_factor=scale_factor,
                                        mode=mode)

        mid_channels = max(in_channels//channel_factor, 1)
        conv_1 = conv(in_channels,
                      mid_channels,
                      1,
                      stride=1,
                      padding=0,
                      bias=bias)
        conv_2 = conv(mid_channels,
                      mid_channels,
                      kernel_size,
                      stride=stride,
                      padding=padding,
                      bias=bias,
                      padding_mode=padding_mode)
        if use_double_conv == True:
            conv_3 = conv(mid_channels,
                          mid_channels,
                          kernel_size,
                          stride=stride,
                          padding=padding,
                          bias=bias,
                          padding_mode=padding_mode)
        conv_4 = conv(mid_channels,
                      out_channels,
                      1,
                      stride=1,
                      padding=0,
                      bias=bias)
        if weight_normalization is not None:
            for norm in weight_normalization:
                conv_1 = norm(conv_1)
            for norm in weight_normalization:
                conv_2 = norm(conv_2)
            if use_double_conv == True:
                for norm in weight_normalization:
                    conv_3 = norm(conv_3)
            for norm in weight_normalization:
                conv_4 = norm(conv_4)

        self.main = []
        if layer_normalization is not None:
            self.main += [layer_normalization(in_channels)]
        self.main += [activation(),
                      conv_1]
        if layer_normalization is not None:
            self.main += [layer_normalization(mid_channels)]
        self.main += [activation(),
                      nn.Upsample(scale_factor=scale_factor,
                                  mode=mode),
                      conv_2]
        if use_double_conv == True:
            if layer_normalization is not None:
                self.main += [layer_normalization(mid_channels)]
            self.main += [activation(),
                        conv_3]
        if layer_normalization is not None:
            self.main += [layer_normalization(mid_channels)]
        self.main += [activation(),
                      conv_4]
        self.main = BlockSequential(*self.main)

    def forward(self, input, label=None):
        
        output = self.main(input, label)
        residual = input
        if self.shortcut is not None:
            residual = residual[:, :output.shape[1]]
            residual = self.shortcut(residual)

        return residual + self.residual_weight*output


class DeepResBlockUpscale2d(_DeepResBlockUpscale):
    """
    Deep residual block for upscaling.
    
    Parameters
    ----------
    in_channels : int
        Number of channels in the input image.
    out_channels : int
        Number of channels produced by the convolution.
    channel_factor : int, optional (default 4)
        Factor by which to decrease the number of channels in the two middle
        convolution layers.
    scale_factor : int or tuple, optional (default 2)
        Scale factor for upscaling.
    mode : str, optional (default 'nearest')
        Interpolation used for upscaling.
    residual_weight : float, optional (default 1.)
        Weight applied to the residual mapping before addition.
    kernel_size : int or tuple, optional (default 3)
        Size of the convolving kernel.
    stride : int or tuple, optional (default 1)
        Stride of the convolution.
    padding : int or tuple, optional (default 1)
        Zero-padding added to all three sides of the input.
    hidden_channels : int, optional (default None)
        Number of channels used in the intermediate layers when out_channels is 
        different from out_channels.
    bias : bool, optional (default False)
        If True, adds a learnable bias to the output.
    padding_mode : str, optional (default 'zeros')
        Padding mode.
    use_double_conv : bool, optional (default True)
        If True, uses two 3-by-3 convolution layers.
    layer_normalization : nn.Module, optional (default BatchNorm2d)
        Normalization to apply to the output of the convolution (e.g., batch
        normalization).
    weight_normalization : function or array-like of shape (n_norms,), optional (default None)
        Normalization(s) to apply to the weights of the transformation (e.g.,
        spectral normalization).
    activation : nn.Module, optional (default nn.ReLU)
        Activation to apply to the output of the normalization, if any, and the
        convolution otherwise.
    """
    def __init__(self,
                 in_channels,
                 out_channels,
                 channel_factor=4,
                 scale_factor=2,
                 mode='nearest',
                 residual_weight=1.,
                 kernel_size=3,
                 stride=1,
                 padding=1,
                 bias=False,
                 padding_mode='zeros',
                 use_double_conv=True,
                 layer_normalization=nn.BatchNorm2d,
                 weight_normalization=None,
                 activation=partial(nn.ReLU, inplace=True)):

        super(DeepResBlockUpscale2d, self).__init__(nn.Conv2d,
                                                    in_channels,
                                                    out_channels,
                                                    channel_factor=channel_factor,
                                                    scale_factor=scale_factor,
                                                    mode=mode,
                                                    residual_weight=residual_weight,
                                                    kernel_size=kernel_size,
                                                    stride=stride,
                                                    padding=padding,
                                                    bias=bias,
                                                    padding_mode=padding_mode,
                                                    use_double_conv=use_double_conv,
                                                    layer_normalization=layer_normalization,
                                                    weight_normalization=weight_normalization,
                                                    activation=activation)


class DeepResBlockUpscale3d(_DeepResBlockUpscale):
    """
    Deep residual block for upscaling.
    
    Parameters
    ----------
    in_channels : int
        Number of channels in the input image.
    out_channels : int
        Number of channels produced by the convolution.
    channel_factor : int, optional (default 4)
        Factor by which to decrease the number of channels in the two middle
        convolution layers.
    scale_factor : int or tuple, optional (default 2)
        Scale factor for upscaling.
    mode : str, optional (default 'nearest')
        Interpolation used for upscaling.
    residual_weight : float, optional (default 1.)
        Weight applied to the residual mapping before addition.
    kernel_size : int or tuple, optional (default 3)
        Size of the convolving kernel.
    stride : int or tuple, optional (default 1)
        Stride of the convolution.
    padding : int or tuple, optional (default 1)
        Zero-padding added to all three sides of the input.
    hidden_channels : int, optional (default None)
        Number of channels used in the intermediate layers when out_channels is 
        different from out_channels.
    bias : bool, optional (default False)
        If True, adds a learnable bias to the output.
    padding_mode : str, optional (default 'zeros')
        Padding mode.
    use_double_conv : bool, optional (default True)
        If True, uses two 3-by-3 convolution layers.
    layer_normalization : nn.Module, optional (default BatchNorm3d)
        Normalization to apply to the output of the convolution (e.g., batch
        normalization).
    weight_normalization : function or array-like of shape (n_norms,), optional (default None)
        Normalization(s) to apply to the weights of the transformation (e.g.,
        spectral normalization).
    activation : nn.Module, optional (default nn.ReLU)
        Activation to apply to the output of the normalization, if any, and the
        convolution otherwise.
    """
    def __init__(self,
                 in_channels,
                 out_channels,
                 channel_factor=4,
                 scale_factor=2,
                 mode='nearest',
                 residual_weight=1.,
                 kernel_size=3,
                 stride=1,
                 padding=1,
                 bias=False,
                 padding_mode='zeros',
                 use_double_conv=True,
                 layer_normalization=nn.BatchNorm3d,
                 weight_normalization=None,
                 activation=partial(nn.ReLU, inplace=True)):

        super(DeepResBlockUpscale3d, self).__init__(nn.Conv3d,
                                                    in_channels,
                                                    out_channels,
                                                    channel_factor=channel_factor,
                                                    scale_factor=scale_factor,
                                                    mode=mode,
                                                    residual_weight=residual_weight,
                                                    kernel_size=kernel_size,
                                                    stride=stride,
                                                    padding=padding,
                                                    bias=bias,
                                                    padding_mode=padding_mode,
                                                    use_double_conv=use_double_conv,
                                                    layer_normalization=layer_normalization,
                                                    weight_normalization=weight_normalization,
                                                    activation=activation)


class _DeepResBlockDownscale(nn.Module):
    """
    Deep residual block for downscaling.
    
    Parameters
    ----------
    conv : nn.Module
        Convolution to apply.
    in_channels : int
        Number of channels in the input image.
    out_channels : int
        Number of channels produced by the convolution.
    channel_factor : int, optional (default 4)
        Factor by which to decrease the number of channels in the two middle
        convolution layers.
    scale_factor : int or tuple, optional (default 2)
        Scale factor for downscaling.
    residual_weight : float, optional (default 1.)
        Weight applied to the residual mapping before addition.
    kernel_size : int or tuple, optional (default 3)
        Size of the convolving kernel.
    stride : int or tuple, optional (default 1)
        Stride of the convolution.
    padding : int or tuple, optional (default 1)
        Zero-padding added to all three sides of the input.
    hidden_channels : int, optional (default None)
        Number of channels used in the intermediate layers when out_channels is 
        different from out_channels.
    bias : bool, optional (default False)
        If True, adds a learnable bias to the output.
    padding_mode : str, optional (default 'zeros')
        Padding mode.
    use_double_conv : bool, optional (default True)
        If True, uses two 3-by-3 convolution layers.
    layer_normalization : nn.Module, optional (default None)
        Normalization to apply to the output of the convolution (e.g., batch
        normalization).
    weight_normalization : function or array-like of shape (n_norms,), optional (default None)
        Normalization(s) to apply to the weights of the transformation (e.g.,
        spectral normalization).
    activation : nn.Module, optional (default nn.ReLU)
        Activation to apply to the output of the normalization, if any, and the
        convolution otherwise.
    """
    def __init__(self,
                 conv,
                 downscale,
                 in_channels,
                 out_channels,
                 channel_factor=4,
                 scale_factor=2,
                 residual_weight=1.,
                 kernel_size=3,
                 stride=1,
                 padding=1,
                 bias=False,
                 padding_mode='zeros',
                 use_double_conv=True,
                 layer_normalization=None,
                 weight_normalization=None,
                 activation=partial(nn.ReLU, inplace=True)):

        super(_DeepResBlockDownscale, self).__init__()

        if isinstance(layer_normalization, _BatchNorm):
            bias = False
        if (weight_normalization is not None and
            isinstance(weight_normalization, (tuple, list)) == False):
            weight_normalization = [weight_normalization]

        scale_factor = _triple(scale_factor)
        stride = _triple(stride)
        self.residual_weight = residual_weight

        self.shortcut_pool = None
        self.shortcut_conv = None
        if any(x > 1 for x in scale_factor) or any(x > 1 for x in stride):
            self.shortcut_pool = downscale(scale_factor)
        if in_channels != out_channels:
            self.shortcut_conv = conv(in_channels,
                                      out_channels - in_channels,
                                      1,
                                      stride=1,
                                      padding=0,
                                      bias=False)
            if weight_normalization is not None:
                for norm in weight_normalization:
                    self.shortcut_conv = norm(self.shortcut_conv)

        mid_channels = max(in_channels//channel_factor, 1)
        conv_1 = conv(in_channels,
                      mid_channels,
                      1,
                      stride=1,
                      padding=0,
                      bias=bias)
        conv_2 = conv(mid_channels,
                      mid_channels,
                      kernel_size,
                      stride=stride,
                      padding=padding,
                      bias=bias,
                      padding_mode=padding_mode)
        if use_double_conv == True:
            conv_3 = conv(mid_channels,
                          mid_channels,
                          kernel_size,
                          stride=stride,
                          padding=padding,
                          bias=bias,
                          padding_mode=padding_mode)
        conv_4 = conv(mid_channels,
                      out_channels,
                      1,
                      stride=1,
                      padding=0,
                      bias=bias)
        if weight_normalization is not None:
            for norm in weight_normalization:
                conv_1 = norm(conv_1)
            for norm in weight_normalization:
                conv_2 = norm(conv_2)
            if use_double_conv == True:
                for norm in weight_normalization:
                    conv_3 = norm(conv_3)
            for norm in weight_normalization:
                conv_4 = norm(conv_4)

        self.main = []
        if layer_normalization is not None:
            self.main += [layer_normalization(in_channels)]
        self.main += [activation(),
                      conv_1]
        if layer_normalization is not None:
            self.main += [layer_normalization(mid_channels)]
        self.main += [activation(),
                      conv_2]
        if use_double_conv == True:
            if layer_normalization is not None:
                self.main += [layer_normalization(mid_channels)]
            self.main += [activation(),
                        conv_3]
        if layer_normalization is not None:
            self.main += [layer_normalization(mid_channels)]
        self.main += [activation(),
                      downscale(scale_factor),
                      conv_4]
        self.main = BlockSequential(*self.main)

    def forward(self, input, label=None):
        
        output = self.main(input, label)
        residual = input
        if self.shortcut_pool is not None:
            residual = self.shortcut_pool(input)
        if self.shortcut_conv is not None:
            residual = torch.cat([residual, self.shortcut_conv(residual)], dim=1)

        return residual + self.residual_weight*output


class DeepResBlockDownscale2d(_DeepResBlockDownscale):
    """
    Deep residual block for downscaling.
    
    Parameters
    ----------
    in_channels : int
        Number of channels in the input image.
    out_channels : int
        Number of channels produced by the convolution.
    channel_factor : int, optional (default 4)
        Factor by which to decrease the number of channels in the two middle
        convolution layers.
    scale_factor : int or tuple, optional (default 2)
        Scale factor for downscaling.
    residual_weight : float, optional (default 1.)
        Weight applied to the residual mapping before addition.
    kernel_size : int or tuple, optional (default 3)
        Size of the convolving kernel.
    stride : int or tuple, optional (default 1)
        Stride of the convolution.
    padding : int or tuple, optional (default 1)
        Zero-padding added to all three sides of the input.
    hidden_channels : int, optional (default None)
        Number of channels used in the intermediate layers when out_channels is 
        different from out_channels.
    bias : bool, optional (default False)
        If True, adds a learnable bias to the output.
    padding_mode : str, optional (default 'zeros')
        Padding mode.
    use_double_conv : bool, optional (default True)
        If True, uses two 3-by-3 convolution layers.
    layer_normalization : nn.Module, optional (default BatchNorm2d)
        Normalization to apply to the output of the convolution (e.g., batch
        normalization).
    weight_normalization : function or array-like of shape (n_norms,), optional (default None)
        Normalization(s) to apply to the weights of the transformation (e.g.,
        spectral normalization).
    activation : nn.Module, optional (default nn.ReLU)
        Activation to apply to the output of the normalization, if any, and the
        convolution otherwise.
    """
    def __init__(self,
                 in_channels,
                 out_channels,
                 channel_factor=4,
                 scale_factor=2,
                 residual_weight=1.,
                 kernel_size=3,
                 stride=1,
                 padding=1,
                 bias=False,
                 padding_mode='zeros',
                 use_double_conv=True,
                 layer_normalization=nn.BatchNorm2d,
                 weight_normalization=None,
                 activation=partial(nn.ReLU, inplace=True)):

        super(DeepResBlockDownscale2d, self).__init__(nn.Conv2d,
                                                      nn.AvgPool2d,
                                                      in_channels,
                                                      out_channels,
                                                      channel_factor=channel_factor,
                                                      scale_factor=scale_factor,
                                                      residual_weight=residual_weight,
                                                      kernel_size=kernel_size,
                                                      stride=stride,
                                                      padding=padding,
                                                      bias=bias,
                                                      padding_mode=padding_mode,
                                                      use_double_conv=use_double_conv,
                                                      layer_normalization=layer_normalization,
                                                      weight_normalization=weight_normalization,
                                                      activation=activation)


class DeepResBlockDownscale3d(_DeepResBlockDownscale):
    """
    Deep residual block for downscaling.
    
    Parameters
    ----------
    in_channels : int
        Number of channels in the input image.
    out_channels : int
        Number of channels produced by the convolution.
    channel_factor : int, optional (default 4)
        Factor by which to decrease the number of channels in the two middle
        convolution layers.
    scale_factor : int or tuple, optional (default 2)
        Scale factor for downscaling.
    residual_weight : float, optional (default 1.)
        Weight applied to the residual mapping before addition.
    kernel_size : int or tuple, optional (default 3)
        Size of the convolving kernel.
    stride : int or tuple, optional (default 1)
        Stride of the convolution.
    padding : int or tuple, optional (default 1)
        Zero-padding added to all three sides of the input.
    hidden_channels : int, optional (default None)
        Number of channels used in the intermediate layers when out_channels is 
        different from out_channels.
    bias : bool, optional (default False)
        If True, adds a learnable bias to the output.
    padding_mode : str, optional (default 'zeros')
        Padding mode.
    use_double_conv : bool, optional (default True)
        If True, uses two 3-by-3 convolution layers.
    layer_normalization : nn.Module, optional (default BatchNorm3d)
        Normalization to apply to the output of the convolution (e.g., batch
        normalization).
    weight_normalization : function or array-like of shape (n_norms,), optional (default None)
        Normalization(s) to apply to the weights of the transformation (e.g.,
        spectral normalization).
    activation : nn.Module, optional (default nn.ReLU)
        Activation to apply to the output of the normalization, if any, and the
        convolution otherwise.
    """
    def __init__(self,
                 in_channels,
                 out_channels,
                 channel_factor=4,
                 scale_factor=2,
                 residual_weight=1.,
                 kernel_size=3,
                 stride=1,
                 padding=1,
                 bias=False,
                 padding_mode='zeros',
                 use_double_conv=True,
                 layer_normalization=nn.BatchNorm3d,
                 weight_normalization=None,
                 activation=partial(nn.ReLU, inplace=True)):

        super(DeepResBlockDownscale3d, self).__init__(nn.Conv3d,
                                                      nn.AvgPool3d,
                                                      in_channels,
                                                      out_channels,
                                                      channel_factor=channel_factor,
                                                      scale_factor=scale_factor,
                                                      residual_weight=residual_weight,
                                                      kernel_size=kernel_size,
                                                      stride=stride,
                                                      padding=padding,
                                                      bias=bias,
                                                      padding_mode=padding_mode,
                                                      use_double_conv=use_double_conv,
                                                      layer_normalization=layer_normalization,
                                                      weight_normalization=weight_normalization,
                                                      activation=activation)


################################################################################
# Self-attention

class _SelfAttentionBlock(nn.Module):
    """
    Self-attention block.
    
    Parameters
    ----------
    conv : nn.Module
        Convolution to apply.
    max_pool : nn.Module
        Max pool to apply.
    in_channels : int
        Number of channels in the input image.
    feature_size : int, optional (default 8)
        Size of the feature maps.
    scale_factor : int or tuple, optional (default 2)
        Scale factor for downscaling.
    padding : int or tuple, optional (default 1)
        Zero-padding added to all three sides of the input.
    bias : bool, optional (default False)
        If True, adds a learnable bias to the output.
    padding_mode : str, optional (default 'zeros')
        Padding mode.
    weight_normalization : function or array-like of shape (n_norms,), optional (default None)
        Normalization(s) to apply to the weights of the transformation (e.g.,
        spectral normalization).

    References
    ----------
    Zhang, H., Goodfellow, I., Metaxas, D., Odena, A. (2018).
        Self-Attention Generative Adversarial Networks
        arXiv preprint arXiv:1805.08318, https://arxiv.org/abs/1805.08318
    Zhang, H. (2018).
        Self-Attention GAN
        https://github.com/brain-research/self-attention-gan
    Brock, A. (2019).
        BigGAN-PyTorch.
        https://github.com/ajbrock/BigGAN-PyTorch
    """
    def __init__(self,
                 conv,
                 max_pool,
                 in_channels,
                 feature_size=8,
                 scale_factor=2,
                 bias=False,
                 padding_mode='zeros',
                 weight_normalization=None):

        super(_SelfAttentionBlock, self).__init__()

        self.query = conv(in_channels,
                          in_channels//feature_size,
                          1,
                          bias=bias,
                          padding_mode=padding_mode,
                          weight_normalization=weight_normalization)
        self.key = [conv(in_channels,
                         in_channels//feature_size,
                         1,
                         bias=bias,
                         padding_mode=padding_mode,
                         weight_normalization=weight_normalization),
                    max_pool(scale_factor)]
        self.key = nn.Sequential(*self.key)
        self.value = [conv(in_channels,
                           in_channels//2,
                           1,
                           bias=bias,
                           padding_mode=padding_mode,
                           weight_normalization=weight_normalization),
                      max_pool(scale_factor)]
        self.value = nn.Sequential(*self.value)
        self.attention_weight = conv(in_channels//2,
                                     in_channels,
                                     1,
                                     bias=bias,
                                     padding_mode=padding_mode,
                                     weight_normalization=weight_normalization)
        # Learnable gain parameter
        self.gamma = nn.Parameter(torch.tensor(0.), requires_grad=True)

    def forward(self, input, label=None):

        # Apply convs
        query = self.query(input)
        key = self.key(input)
        value = self.value(input)
        # Perform reshapes
        query = query.view(*query.shape[:2], -1)
        key = key.view(*key.shape[:2], -1)
        value = value.view(*value.shape[:2], -1)
        # Matmul and softmax to get attention map
        attention_map = nn.functional.softmax(torch.bmm(query.transpose(1, 2), key), -1)
        # Attention map times g path
        attention_weight = self.attention_weight(torch.bmm(value, attention_map.transpose(1, 2)).view(*value.shape[:2], *input.shape[2:]))

        return self.gamma*attention_weight + input


class SelfAttentionBlock2d(_SelfAttentionBlock):
    """
    Self-attention block.
    
    Parameters
    ----------
    in_channels : int
        Number of channels in the input image.
    feature_size : int, optional (default 8)
        Size of the feature maps.
    scale_factor : int or tuple, optional (default 2)
        Scale factor for downscaling.
    padding : int or tuple, optional (default 1)
        Zero-padding added to all three sides of the input.
    bias : bool, optional (default False)
        If True, adds a learnable bias to the output.
    padding_mode : str, optional (default 'zeros')
        Padding mode.
    weight_normalization : function or array-like of shape (n_norms,), optional (default None)
        Normalization(s) to apply to the weights of the transformation (e.g.,
        spectral normalization).

    References
    ----------
    Zhang, H., Goodfellow, I., Metaxas, D., Odena, A. (2018).
        Self-Attention Generative Adversarial Networks
        arXiv preprint arXiv:1805.08318, https://arxiv.org/abs/1805.08318
    Zhang, H. (2018).
        Self-Attention GAN
        https://github.com/brain-research/self-attention-gan
    Brock, A. (2019).
        BigGAN-PyTorch.
        https://github.com/ajbrock/BigGAN-PyTorch
    """
    def __init__(self,
                 in_channels,
                 feature_size=8,
                 scale_factor=2,
                 bias=False,
                 padding_mode='zeros',
                 weight_normalization=None):

        super(SelfAttentionBlock2d, self).__init__(ConvBlock2d,
                                                   nn.MaxPool2d,
                                                   in_channels,
                                                   feature_size=feature_size,
                                                   scale_factor=scale_factor,
                                                   bias=bias,
                                                   padding_mode=padding_mode,
                                                   weight_normalization=weight_normalization)


class SelfAttentionBlock3d(_SelfAttentionBlock):
    """
    Self-attention block.
    
    Parameters
    ----------
    in_channels : int
        Number of channels in the input image.
    feature_size : int, optional (default 8)
        Size of the feature maps.
    scale_factor : int or tuple, optional (default 2)
        Scale factor for downscaling.
    padding : int or tuple, optional (default 1)
        Zero-padding added to all three sides of the input.
    bias : bool, optional (default False)
        If True, adds a learnable bias to the output.
    padding_mode : str, optional (default 'zeros')
        Padding mode.
    weight_normalization : function or array-like of shape (n_norms,), optional (default None)
        Normalization(s) to apply to the weights of the transformation (e.g.,
        spectral normalization).

    References
    ----------
    Zhang, H., Goodfellow, I., Metaxas, D., Odena, A. (2018).
        Self-Attention Generative Adversarial Networks
        arXiv preprint arXiv:1805.08318, https://arxiv.org/abs/1805.08318
    Zhang, H. (2018).
        Self-Attention GAN
        https://github.com/brain-research/self-attention-gan
    Brock, A. (2019).
        BigGAN-PyTorch.
        https://github.com/ajbrock/BigGAN-PyTorch
    """
    def __init__(self,
                 in_channels,
                 feature_size=8,
                 scale_factor=2,
                 bias=False,
                 padding_mode='zeros',
                 weight_normalization=None):

        super(SelfAttentionBlock3d, self).__init__(ConvBlock3d,
                                                   nn.MaxPool3d,
                                                   in_channels,
                                                   feature_size=feature_size,
                                                   scale_factor=scale_factor,
                                                   bias=bias,
                                                   padding_mode=padding_mode,
                                                   weight_normalization=weight_normalization)
