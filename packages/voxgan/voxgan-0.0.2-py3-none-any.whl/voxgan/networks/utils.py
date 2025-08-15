"""Utils for convolutional neural networks"""

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


import torch
import torch.nn as nn


################################################################################
# nD

class _ConditionalBatchNorm(nn.Module):
    """
    Conditional batch normalization.

    Parameters
    ----------
    batch_norm : nn.Module
        Batch normalization to apply.
    num_features : int
        C from an expected input of size (N,C,D,H).
    num_classes : int
        Number of classes in the conditioning vector.
    embedding : nn.Module, optional (default nn.Linear)
        Embedding for the conditioning vector, usually nn.Embedding or nn.Linear.
    one_centered_gain : bool, optional (default True)
        If true, uses one-centered gains, which is useful when using a linear
        embedding to make initialization easier.
    eps : float, optional (default 1e-05)
        Value added to the denominator for numerical stability.
    momentum : float, optional (default 0.1)
        Value used for the running_mean and running_var computation. Can be set 
        to None for cumulative moving average (i.e. simple average).

    Source
    ------
    https://github.com/pytorch/pytorch/issues/8985#issuecomment-405080775
    """
    def __init__(self,
                 batch_norm,
                 num_features,
                 num_classes,
                 embedding=nn.Linear,
                 one_centered_gain=True,
                 eps=1e-05,
                 momentum=0.1):

        super(_ConditionalBatchNorm, self).__init__()

        self.num_features = num_features
        self.bn = batch_norm(num_features, eps=eps, momentum=momentum, affine=False)
        self.embedding = embedding(num_classes, num_features*2)
        # Initialise scale at N(1, 0.02)
        self.embedding.weight.data[:, :num_features].normal_(1, 0.02)
        # Initialise bias at 0
        self.embedding.weight.data[:, num_features:].zero_()
        self.one_centered_gain = one_centered_gain

    def forward(self, input, label):

        output = self.bn(input)
        gain, bias = self.embedding(label.flatten(1)).chunk(2, 1)
        if self.one_centered_gain == True:
            gain = 1. + gain
        shape = (-1, self.num_features) + (1,)*(len(output.shape) - 2)
        output = gain.view(*shape)*output + bias.view(*shape)

        return output


################################################################################
# 2D

class LayerNorm2D(nn.Module):
    """
    Layer normalization in 2D implemented following the batch normalization API.
    """
    def __init__(self, eps=1e-05, elementwise_affine=True):

        super(LayerNorm2D, self).__init__()

        self.axis = slice(-2, None)
        self.eps = eps
        self.elementwise_affine = elementwise_affine

    def forward(self, input):

        normalized_shape = input.shape[self.axis]
        layer_norm = nn.LayerNorm(normalized_shape,
                                  eps=self.eps,
                                  elementwise_affine=self.elementwise_affine)

        return layer_norm(input)


class BatchNorm2d(nn.BatchNorm2d):
    """
    Batch normalization in 2D.

    Parameters
    ----------
    num_features : int
        C from an expected input of size (N,C,D).
    eps : float, optional (default 1e-05)
        Value added to the denominator for numerical stability.
    momentum : float, optional (default 0.1)
        Value used for the running_mean and running_var computation. Can be set 
        to None for cumulative moving average (i.e. simple average).
    center : bool, optional (default True)
        If True, add offset of beta to normalized tensor.
    scale : bool, optional (default True)
        If True, multiply by gamma.
    affine : bool, optional (default True)
        If True, this module has learnable affine parameters.
    track_running_stats : bool, optional (default True)
        If True, this module tracks the running mean and variance, and when set
        to False, this module does not track such statistics, and initializes
        statistics buffers running_mean and running_var as None. When these
        buffers are None, this module always uses batch statistics. in both
        training and eval modes.
    device : torch.device, optional (default None)
        The torch.device where this layer is.
    dtype : torch.dtype, optional (default None)
        The dtype of the layer.

    Source
    ------
    https://github.com/pytorch/pytorch/pull/40429
    """
    def __init__(self,
                 num_features,
                 eps=1e-05,
                 momentum=0.1,
                 center=True,
                 scale=True,
                 affine=True,
                 track_running_stats=True,
                 device=None,
                 dtype=None):

        super(BatchNorm2d, self).__init__(num_features, eps, momentum, affine,
                                          track_running_stats, device, dtype)
        if scale == False:
            self.weight.requires_grad = False
        if center == False:
            self.bias.requires_grad = False


class ConditionalBatchNorm2d(_ConditionalBatchNorm):
    """
    Conditional batch normalization in 2D.

    Parameters
    ----------
    num_features : int
        C from an expected input of size (N,C,D,H).
    num_classes : int
        Number of classes in the conditioning vector.
    embedding : nn.Module, optional (default nn.Linear)
        Embedding for the conditioning vector, usually nn.Embedding or nn.Linear.
    one_centered_gain : bool, optional (default True)
        If true, uses one-centered gains, which is useful when using a linear
        embedding to make initialization easier.
    eps : float, optional (default 1e-05)
        Value added to the denominator for numerical stability.
    momentum : float, optional (default 0.1)
        Value used for the running_mean and running_var computation. Can be set 
        to None for cumulative moving average (i.e. simple average).

    Source
    ------
    https://github.com/pytorch/pytorch/issues/8985#issuecomment-405080775
    """
    def __init__(self,
                 num_features,
                 num_classes,
                 embedding=nn.Linear,
                 one_centered_gain=True,
                 eps=1e-05,
                 momentum=0.1):

        super(ConditionalBatchNorm2d, self).__init__(nn.BatchNorm2d,
                                                     num_features,
                                                     num_classes,
                                                     embedding=embedding,
                                                     one_centered_gain=one_centered_gain,
                                                     eps=eps,
                                                     momentum=momentum)


################################################################################
# 3D

class LayerNorm3D(nn.Module):
    """
    Layer normalization in 3D implemented following the batch normalization API.
    """
    def __init__(self, eps=1e-05, elementwise_affine=True):

        super(LayerNorm3D, self).__init__()

        self.axis = slice(-3, None)
        self.eps = eps
        self.elementwise_affine = elementwise_affine

    def forward(self, input):

        normalized_shape = input.shape[self.axis]
        layer_norm = nn.LayerNorm(normalized_shape,
                                  eps=self.eps,
                                  elementwise_affine=self.elementwise_affine)

        return layer_norm(input)


class BatchNorm3d(nn.BatchNorm3d):
    """
    Batch normalization in 3D.

    Parameters
    ----------
    num_features : int
        C from an expected input of size (N,C,D,H).
    eps : float, optional (default 1e-05)
        Value added to the denominator for numerical stability.
    momentum : float, optional (default 0.1)
        Value used for the running_mean and running_var computation. Can be set 
        to None for cumulative moving average (i.e. simple average).
    center : bool, optional (default True)
        If True, add offset of beta to normalized tensor.
    scale : bool, optional (default True)
        If True, multiply by gamma.
    affine : bool, optional (default True)
        If True, this module has learnable affine parameters.
    track_running_stats : bool, optional (default True)
        If True, this module tracks the running mean and variance, and when set
        to False, this module does not track such statistics, and initializes
        statistics buffers running_mean and running_var as None. When these
        buffers are None, this module always uses batch statistics. in both
        training and eval modes.
    device : torch.device, optional (default None)
        The torch.device where this layer is.
    dtype : torch.dtype, optional (default None)
        The dtype of the layer.

    Source
    ------
    https://github.com/pytorch/pytorch/pull/40429
    """
    def __init__(self,
                 num_features,
                 eps=1e-05,
                 momentum=0.1,
                 center=True,
                 scale=True,
                 affine=True,
                 track_running_stats=True,
                 device=None,
                 dtype=None):

        super(BatchNorm3d, self).__init__(num_features, eps, momentum, affine,
                                          track_running_stats, device, dtype)
        if scale == False:
            self.weight.requires_grad = False
        if center == False:
            self.bias.requires_grad = False


class ConditionalBatchNorm3d(_ConditionalBatchNorm):
    """
    Conditional batch normalization in 3D.

    Parameters
    ----------
    num_features : int
        C from an expected input of size (N,C,D,H,W).
    num_classes : int
        Number of classes in the conditioning vector.
    embedding : nn.Module, optional (default nn.Linear)
        Embedding for the conditioning vector, usually nn.Embedding or nn.Linear.
    one_centered_gain : bool, optional (default True)
        If true, uses one-centered gains, which is useful when using a linear
        embedding to make initialization easier.
    eps : float, optional (default 1e-05)
        Value added to the denominator for numerical stability.
    momentum : float, optional (default 0.1)
        Value used for the running_mean and running_var computation. Can be set 
        to None for cumulative moving average (i.e. simple average).

    Source
    ------
    https://github.com/pytorch/pytorch/issues/8985#issuecomment-405080775
    """
    def __init__(self,
                 num_features,
                 num_classes,
                 embedding=nn.Linear,
                 one_centered_gain=True,
                 eps=1e-05,
                 momentum=0.1):

        super(ConditionalBatchNorm3d, self).__init__(nn.BatchNorm3d,
                                                     num_features,
                                                     num_classes,
                                                     embedding=embedding,
                                                     one_centered_gain=one_centered_gain,
                                                     eps=eps,
                                                     momentum=momentum)


################################################################################
# Initialization

def initialize_weights_normal(module, std=0.02):
    """
    Randomly initializes all weights of the convolution and batch
    normalization layers of the generator and discriminator.
    """
    if (isinstance(module, (nn.Conv2d, nn.ConvTranspose2d,
                            nn.Conv3d, nn.ConvTranspose3d,
                            nn.Linear, nn.Embedding)) and
        module.weight is not None):
        nn.init.normal_(module.weight.data, 0., std)
    elif (isinstance(module, (nn.BatchNorm2d, nn.BatchNorm3d)) and
          module.weight is not None):
        nn.init.normal_(module.weight.data, 1., std)
        nn.init.constant_(module.bias.data, 0.)


def initialize_weights(module, initializer_conv, initializer_batchnorm):
    """
    Randomly initializes all weights of the convolution and batch
    normalization layers of the generator and discriminator.
    """
    if (isinstance(module, (nn.Conv2d, nn.ConvTranspose2d,
                            nn.Conv3d, nn.ConvTranspose3d,
                            nn.Linear, nn.Embedding)) and
        module.weight is not None):
        initializer_conv(module.weight.data)
    elif (isinstance(module, (nn.BatchNorm2d, nn.BatchNorm3d)) and
          module.weight is not None):
        initializer_batchnorm(module.weight.data)
        nn.init.constant_(module.bias.data, 0.)


################################################################################
# Training

class EMA(torch.optim.swa_utils.AveragedModel):
    """
    Exponential Moving Average.

    Parameters
    ----------
    model : torch.nn.Module
        Model to use with EMA.
    decay : float, optional (default 0.9999)
        Decay to apply to the averaging.
    device : torch.device, optional (default None):
        If provided, the averaged model will be stored on the `device`.
    use_buffers : bool, optional (default False)
        If True, it will compute running averages for both the parameters and
        the buffers of the model.
    """
    def __init__(self, model, decay=0.9999, device=None, use_buffers=False):

        super(EMA, self).__init__(model, device=device, avg_fn=self._ema_avg, use_buffers=use_buffers)
        self.decay = decay

    def _ema_avg(self, averaged_model_parameter, model_parameter, num_averaged):
        """
        Averages the model weights with a decay.
        """
        return self.decay*averaged_model_parameter + (1. - self.decay)*model_parameter
