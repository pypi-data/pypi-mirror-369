"""Metrics"""

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
from torch.nn import functional as F
import torch.nn as nn
from torch.utils.data import DataLoader


################################################################################
# Base metric

class BaseMetric:
    """
    Base class for metrics.
    
    Parameters
    ----------
    batch_size : int, optional (default None)
        Batch size to compute the metric. Only used when `input` or `target` in
        `__call__` is a function generating samples from a single parameter, the
        number of samples, which is equal to the batch size here. When None, it
        is inferred from `input` or `target`, if one is a tensor or a DataLoader.
    n_samples : int, optional (default None)
        Number of validation samples. Only used when `input` or `target` in
        `__call__` is a function generating samples from a single parameter, the
        number of samples, which is equal to the batch size here. When None, it
        is inferred from `input` or `target`, if one is a tensor or a DataLoader.
    n_gpu : int, optional (default 0)
        Number of GPUs available. If this is 0, code will run in CPU mode. If 
        this number is greater than 0 it will run on that number of GPUs.
    """
    def __init__(self,
                 batch_size=None,
                 n_samples=None,
                 n_gpu=0):

        self.batch_size = batch_size
        self.n_samples = n_samples
        if torch.cuda.is_available():
            self.n_gpu = torch.cuda.device_count() if n_gpu == -1 else n_gpu
        else:
            self.n_gpu = 0
    
    def _infer_parameters(self, input, target):

        if callable(input) == True and callable(target) == False:
            if isinstance(target, (tuple, list)) == True or torch.is_tensor(target) == True:
                self.n_samples = len(target)
            elif isinstance(target, dict) == True:
                self.n_samples = len(target['data'])
            elif isinstance(target, DataLoader) == True:
                self.batch_size = target.batch_size
                self.n_samples = len(target.dataset)
        if callable(input) == False and callable(target) == True:
            if isinstance(input, (tuple, list)) == True or torch.is_tensor(input) == True:
                self.n_samples = len(input)
            elif isinstance(input, dict) == True:
                self.n_samples = len(input['data'])
            elif isinstance(input, DataLoader) == True:
                self.batch_size = input.batch_size
                self.n_samples = len(input.dataset)
    
    def _partial_transform(self, samples, device):

        raise NotImplementedError

    def _transform(self, samples, device, dim=0):

        if torch.is_tensor(samples) == True:
            return self._partial_transform(samples, device)
        elif isinstance(samples, DataLoader) == True:
            outputs = []
            for batch in samples:
                outputs.append(self._partial_transform(batch['data'], device))
            return torch.cat(outputs, dim=dim)
        elif callable(samples) == True:
            outputs = []
            for i in range(0, self.n_samples, self.batch_size):
                b_size = min(self.batch_size, self.n_samples - i)
                outputs.append(self._partial_transform(samples(b_size)['data'], device))
            return torch.cat(outputs, dim=dim)
        
    def __call__(self, input, target):

        self._infer_parameters(input, target)

        raise NotImplementedError


################################################################################
# Multi-scale sliced Wasserstein distance

# Downsampling/upsampling

def convolve_1D_kernel(kernel, n_dim=2):
    """
    Convolves a 1D kernel into a 2D or 3D kernel.
    """
    if n_dim == 1:
        return kernel
    
    kernel = kernel[None]
    if n_dim == 2:
        return kernel.T@kernel
    elif n_dim == 3:
        return (kernel.T@kernel)[..., None]@kernel


def linear_kernel(n_dim=2, device=None):
    """
    Builds a 1D, 2D, or 3D linear kernel.
    """
    kernel = torch.tensor((0.25, 0.5 , 0.25), device=device)
    
    return convolve_1D_kernel(kernel, n_dim=n_dim)


def equivalent_weighting_kernel(a=0.4, n_dim=2, device=None):
    """
    Builds a 1D, 2D, or 3D equivalent weighting kernel for a Laplacian pyramid.
    """
    kernel = torch.tensor((0.25 - 0.5*a, 0.25, a, 0.25, 0.25 - 0.5*a), device=device)

    return convolve_1D_kernel(kernel, n_dim=n_dim)


def binomial_kernel(n_autoconv=4, n_dim=2, device=None):
    """
    Builds a 1D, 2D, or 3D binomial kernel.
    """
    if n_autoconv == 4:
        kernel = torch.tensor((1., 4., 6., 4., 1.), device=device)/16.
    else:
        kernel = torch.ones(2, device=device)
        for i in range(n_autoconv - 1):
            kernel = F.conv1d(kernel.view(1, 1, -1), torch.ones(1, 1, 2, device=device), padding=1).view(-1)
        kernel /= torch.sum(kernel)

    return convolve_1D_kernel(kernel, n_dim=n_dim)


def downsample(x, kernel, padding_mode='reflect', step=2):
    """
    Downsamples a nD array by convolution using a mD kernel (n >= m) and subsampling.
    """ 
    if kernel.ndim == 1:
        conv = F.conv1d
    elif kernel.ndim == 2:
        conv = F.conv2d
    elif kernel.ndim == 3:
        conv = F.conv3d
    else:
        raise RuntimeError('Only 1, 2 and 3 dimensions are supported. Received {}.'.format(kernel.ndim))
    
    nc = x.shape[1]
    pad = [max(1, size//2) for pair in zip(kernel.shape, kernel.shape) for size in pair]
    x = F.pad(x, pad, mode=padding_mode)
    # Reshape to depthwise convolutional weight
    kernel = kernel.view(1, 1, *kernel.size())
    kernel = kernel.repeat(nc, *[1]*(kernel.dim() - 1))
    
    return conv(x, weight=kernel, stride=step, groups=nc)


def upsample(x, kernel, padding_mode='reflect', step=2, device=None):
    """
    Upsamples a nD array by upsampling and convolution using a mD kernel (n >= m).
    """
    if device is None:
        device = x.device
    n_dim = kernel.ndim
    if n_dim == 1:
        conv = F.conv1d
    elif n_dim == 2:
        conv = F.conv2d
    elif n_dim == 3:
        conv = F.conv3d
    else:
        raise RuntimeError('Only 1, 2 and 3 dimensions are supported. Received {}.'.format(n_dim))
        
    new_shape = tuple(size if i < 2 else step*size
                      for i, size in enumerate(x.shape))
    new_x = torch.zeros(new_shape, device=device)
    slices = tuple(slice(None) if i < 2 else slice(None, None, step)
                   for i in range(x.ndim))
    new_x[slices] = x
    
    nc = x.shape[1]
    pad = [max(1, size//2) for pair in zip(kernel.shape, kernel.shape) for size in pair]
    new_x = F.pad(new_x, pad, mode=padding_mode)
    # Reshape to depthwise convolutional weight
    kernel = kernel.view(1, 1, *kernel.size())
    kernel = kernel.repeat(nc, *[1]*(kernel.dim() - 1))
    
    return 2**n_dim * conv(new_x, weight=kernel, groups=nc)


# Laplacian pyramid

def build_laplacian_pyramid(x, n_levels=3, n_dim=2, kernel=None, padding_mode='reflect', device=None):
    """
    Builds a Laplacian pyramid using a binomial kernel by default.
    """
    if device is None:
        device = x.device
    if kernel is None:
        kernel = binomial_kernel(n_dim=n_dim, device=device)
    
    pyramid = [torch.squeeze(x, tuple(range(2, x.ndim))).clone().to(device)]
    for i in range(1, n_levels):
        pyramid.append(downsample(pyramid[-1], kernel, padding_mode=padding_mode).to(device))
        pyramid[-2] -= upsample(pyramid[-1], kernel, padding_mode=padding_mode, device=device)
        
    return pyramid


# Descriptors

def extract_descriptors(samples, n_descriptors=128, descriptor_size=7, device=None):
    """
    Extracts descriptors from a set of samples.
    """
    if device is None:
        device = samples.device
    if isinstance(descriptor_size, (tuple, list)) == False:
        descriptor_size = (descriptor_size,)*(samples.ndim - 2)
    
    shape = samples.shape
    n_data = n_descriptors*shape[0]
    new_shape = (n_data, shape[1]) + descriptor_size
    grid = []
    for i, size in enumerate(new_shape):
        axis_shape = tuple(1 if j != i else size for j in range(len(new_shape)))
        axis = torch.arange(size, device=device).reshape(axis_shape)
        grid.append(axis)
    
    coord_shape = (n_data, 1) + tuple(1 for size in descriptor_size)
    idx = (grid[0]//n_descriptors)*shape[1] + grid[1]
    for i, size in enumerate(descriptor_size):
        grid[2 + i] = grid[2 + i] + torch.randint(0,
                                                  shape[2 + i] - size,
                                                  size=coord_shape,
                                                  device=device)
        idx = idx*shape[2 + i] + grid[2 + i]

    return torch.take(samples, idx)


def standardize_descriptors(descriptors):
    """
    Standardizes and reshapes a set of descriptors.
    """ 
    axis = (0,) + tuple(i + 2 for i in range(descriptors.ndim - 2))
    descriptors = descriptors - torch.mean(descriptors, dim=axis, keepdim=True)
    descriptors /= torch.std(descriptors, dim=axis, keepdim=True)
    
    return descriptors.reshape(descriptors.shape[0], -1)


# Sliced Wasserstein distance

def _sliced_wasserstein_distance(u, v, n_proj=512, device=None):
    """
    Computes the sliced Wasserstein distance between two point sets.
    """
    if device is None:
        device = u.device
    # Random projections
    proj_matrix = torch.randn(u.shape[1], n_proj, device=device)
    proj_matrix /= torch.sqrt(torch.sum(proj_matrix**2, dim=0, keepdim=True))
    u_proj = torch.matmul(u, proj_matrix)
    v_proj = torch.matmul(v, proj_matrix)
    # Wasserstein distances
    u_proj, _ = torch.sort(u_proj, dim=0)
    v_proj, _ = torch.sort(v_proj, dim=0)
    distances = torch.abs(u_proj - v_proj)
    
    return torch.mean(distances)


def sliced_wasserstein_distance(u, v, n_repeat=4, n_proj=128, device=None):
    """
    Computes the sliced Wasserstein distance between two point sets. Repeating the
    projections decreases memory consumption.
    """
    if device is None:
        device = u.device
    distances = torch.zeros(n_repeat, device=device)
    for i in range(n_repeat):
        distances[i] = _sliced_wasserstein_distance(u, v, n_proj=n_proj)
    
    return torch.mean(distances)


class MSSWD(BaseMetric):
    """
    Computes the multi-scale sliced Wasserstein distance.
    
    Parameters
    ----------
    n_levels : int, optional (default 3)
        Number of levels for the Laplacian pyramid.
    n_descriptors : int, optional (default 128)
        Number of descriptors to extract from each sample.
    descriptor_size : tuple, optional (default (7, 7))
        Size of the descriptors.
    n_repeat : int, optional (default 4)
        Number of times to repeat the projections.
    n_repeat : str, optional (default 'reflect')
        Padding mode for the Laplacian pyramid.
    n_proj : int, optional (default 128)
        Number of projections per repetition. The total number of projections is
        n_repeat*n_proj (default 512).
    padding_mode : str, optional (default 'reflect')
        Padding mode for the down- and upsampling of the Laplacian pyramid.
    combine_levels : bool, optional (default True)
        If True, averages the distance values for each level of the Laplacian
        pyramid into a single value.
    channel : int or slice, optional (default None)
        Channel to consider when computing the distance.
    batch_size : int, optional (default None)
        Batch size to compute the metric. Only used when `input` or `target` in
        `__call__` is a function generating samples from a single parameter, the
        number of samples, which is equal to the batch size here. When None, it
        is inferred from `input` or `target`, if one is a tensor or a DataLoader.
    n_samples : int, optional (default None)
        Number of validation samples. Only used when `input` or `target` in
        `__call__` is a function generating samples from a single parameter, the
        number of samples, which is equal to the batch size here. When None, it
        is inferred from `input` or `target`, if one is a tensor or a DataLoader.
    n_gpu : int, optional (default 0)
        Number of GPUs available. If this is 0, code will run in CPU mode. If 
        this number is greater than 0 it will run on that number of GPUs.

    References
    ----------
    Karras, T., Aila, T., Laine, L., Lehtinen, J. (2017).
        Progressive Growing of GANs for Improved Quality, Stability, and Variation
        arXiv preprint arXiv:1710.10196, https://arxiv.org/abs/1710.10196
    """
    def __init__(self,
                 n_levels=3,
                 n_descriptors=128,
                 descriptor_size=(7, 7),
                 n_repeat=4,
                 n_proj=128,
                 padding_mode='reflect',
                 combine_levels=True,
                 channel=None,
                 batch_size=None,
                 n_samples=None,
                 n_gpu=0):

        super(MSSWD, self).__init__(batch_size, n_samples, n_gpu)

        self.n_levels = n_levels
        self.n_descriptors = n_descriptors
        self.descriptor_size = tuple(x for x in descriptor_size if x != 1)
        self.n_repeat = n_repeat
        self.n_proj = n_proj
        self.padding_mode = padding_mode
        self.combine_levels = combine_levels
        self.channel = channel if channel is not None else slice(None)
        if isinstance(self.channel, int) == True:
            self.channel = slice(self.channel, self.channel + 1)
        
        self._n_dim = len(self.descriptor_size)

    def __str__(self):

        return 'MS-SWD'
    
    def _partial_transform(self, samples, device):

        pyramid = build_laplacian_pyramid(samples[:, self.channel].to(device),
                                          n_levels=self.n_levels,
                                          n_dim=self._n_dim,
                                          padding_mode=self.padding_mode)
        descriptors = torch.empty(self.n_levels,
                                  samples.shape[0]*self.n_descriptors,
                                  samples[:, self.channel].shape[1],
                                  *self.descriptor_size,
                                  device=device)
        for i in range(self.n_levels):
            descriptors[i] = extract_descriptors(pyramid[i],
                                                 self.n_descriptors,
                                                 self.descriptor_size)
        
        return descriptors
        
    def _scatter(self, descriptors_input, descriptors_target):

        descriptor_levels = []
        device_ids = list(range(self.n_gpu))*(self.n_levels//self.n_gpu + 1)
        for l in range(self.n_levels):
            device = torch.device('cuda:' + str(device_ids[l]))
            temp_input = descriptors_input[l].to(device)
            temp_target = descriptors_target[l].to(device)
            descriptor_levels.append(((temp_input, temp_target),))

        return descriptor_levels

    def _distance(self, descriptors):

        descriptors_input = standardize_descriptors(descriptors[0])
        descriptors_target = standardize_descriptors(descriptors[1])
        
        return sliced_wasserstein_distance(descriptors_input,
                                           descriptors_target,
                                           n_repeat=self.n_repeat,
                                           n_proj=self.n_proj)
        
    def __call__(self, input, target):

        self._infer_parameters(input, target)

        with torch.no_grad():
            if self.n_gpu > 1:
                descriptors = nn.parallel.parallel_apply((self._transform, self._transform),
                                                         (input, target),
                                                         ({'device': torch.device('cuda:0'), 'dim': 1},
                                                          {'device': torch.device('cuda:1'), 'dim': 1}))
                replicas = [self._distance for i in range(self.n_levels)]
                descriptor_levels = self._scatter(descriptors[0], descriptors[1])
                distances = nn.parallel.parallel_apply(replicas, descriptor_levels)
                distances = torch.tensor(distances)
            else:
                device = torch.device('cuda:0') if self.n_gpu > 0 else torch.device('cpu')
                descriptors_input = self._transform(input, device, dim=1)
                descriptors_target = self._transform(target, device, dim=1)
                distances = torch.empty(self.n_levels)
                for l in range(self.n_levels):
                    std_descriptors_input = standardize_descriptors(descriptors_input[l])
                    std_descriptors_target = standardize_descriptors(descriptors_target[l])
                    distances[l] = sliced_wasserstein_distance(std_descriptors_input,
                                                               std_descriptors_target,
                                                               n_repeat=self.n_repeat,
                                                               n_proj=self.n_proj)

            if self.combine_levels == True:
                return torch.mean(distances).cpu().numpy()
            return distances.cpu().numpy()


################################################################################
# Law of superposition

class LoS(BaseMetric):
    """
    Checks the law of superposition.
    
    Parameters
    ----------
    channel : int, optional (default 1)
        Channel containing the geological time property.
    batch_size : int, optional (default None)
        Batch size to compute the metric. Only used when `input` or `target` in
        `__call__` is a function generating samples from a single parameter, the
        number of samples, which is equal to the batch size here. When None, it
        is inferred from `input` or `target`, if one is a tensor or a DataLoader.
    n_samples : int, optional (default None)
        Number of validation samples. Only used when `input` or `target` in
        `__call__` is a function generating samples from a single parameter, the
        number of samples, which is equal to the batch size here. When None, it
        is inferred from `input` or `target`, if one is a tensor or a DataLoader.
    n_gpu : int, optional (default 0)
        Number of GPUs available. If this is 0, code will run in CPU mode. If 
        this number is greater than 0 it will run on that number of GPUs.
    """
    def __init__(self, channel=1, batch_size=None, n_samples=None, n_gpu=0):

        super(LoS, self).__init__(batch_size, n_samples, n_gpu)

        self.channel = channel

    def __str__(self):

        return 'LoS'
    
    def _partial_transform(self, samples, device):

        samples = samples.to(device)
        axes = tuple(range(samples[:, self.channel].ndim))[1:]

        return torch.sum(samples[:, self.channel, 1:] >= samples[:, self.channel, :-1], axis=axes)/samples[0, self.channel, 1:].nelement()
        
    def __call__(self, input, target=None):

        self._infer_parameters(input, target)

        with torch.no_grad():
            device = torch.device('cuda:0') if self.n_gpu > 0 else torch.device('cpu')
            distances = self._transform(input, device)

            return torch.mean(distances).cpu().numpy()
