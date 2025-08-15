"""Datasets to handle training data"""

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


from os import path
from glob import glob
import h5py
import numpy as np
from bottleneck import push

import torch
from torch.distributions.uniform import Uniform
from torch.utils.data import Dataset, TensorDataset
from torch.utils import data


################################################################################
# Datasets

class BasicDataset(TensorDataset):
    """
    Dataset from tensors.

    Parameters
    ----------
    tensors : Tensor
        A tensor containing the data, and an optional extra tensor containing
        the labels
    """
    def __init__(self, *tensors):

        super().__init__(*tensors)

    def __getitem__(self, index):

        _sample = super().__getitem__(index)
        sample = {'data': _sample[0]}
        if len(_sample) > 1:
            sample['labels'] = _sample[1]

        return sample


class HDF5Dataset(Dataset):
    """
    Dataset to read HDF5 datasets in which each sample is its own HDF5 file.
    
    Parameters
    ----------
    root : str
        Path to the folder containing the hdf5 files.
    transform : Transform object, optional (default None)
        Transform to apply to a sample before returning it.
    file_paths : array-like of shape (n_files,), optional (default None)
        Paths of the samples that should be part of the dataset. If not None,
        then `root` is ignored.
    """
    def __init__(self, root, transform=None, file_paths=None):
        if path.isdir(root) == False:
            raise ValueError("root isn't valid path.")

        self.file_paths = glob(path.join(root, '*.h5')) if file_paths is None else file_paths
        self.len = len(self.file_paths)
        self.transform = transform

    def __len__(self):
        """
        Length of the dataset.
        """
        return self.len

    def __getitem__(self, idx):
        """
        Gets an item from the dataset.
        """
        if torch.is_tensor(idx):
            idx = idx.tolist()

        with h5py.File(self.file_paths[idx], 'r') as file:
            sample = {'data': file['model'][:]}

        if self.transform is not None:
            sample = self.transform(sample)

        return sample


class HDF5SingleDataset(Dataset):
    """
    Dataset to read HDF5 datasets in a single HDF5 file in which each sample is
    its own dataset, i.e., is accessed through a key.
    
    Parameters
    ----------
    file_path : str
        Path to the hdf5 file.
    transform : Transform object, optional (default None)
        Transform to apply to a sample before returning it.
    """
    def __init__(self, file_path, transform=None):
    
        # self.file = None
        self.file_path = file_path
        with h5py.File(self.file_path, 'r') as file:
            self.keys = list(file.keys())
            self.len = len(file)
        self.transform = transform

    def __len__(self):
        """
        Length of the dataset.
        """
        return self.len

    def __getitem__(self, idx):
        """
        Gets an item from the dataset.
        """
        if torch.is_tensor(idx):
            idx = idx.tolist()

        # Opening the file in init doesn't work with parallel data loading.
        # This is supposed to do the trick, but I can't get it to work.
        # Opening the file at each getitem is supposed to be slow, but it's
        # actually the fastest solution I've found.    
        if not hasattr(self, 'file'):
            self.file = h5py.File(self.file_path, 'r')
        sample = {'data': self.file[self.keys[idx]][:]}
        # with h5py.File(self.file_path, 'r') as file:
        #     sample = {'data': file[self.keys[idx]][:]}

        if self.transform is not None:
            sample = self.transform(sample)

        return sample


class DictDataset(Dataset):
    """
    Dataset to read samples in a dictionary.
    
    Parameters
    ----------
    samples : dictionary
        Dictionary containing the sample data under the key 'data' and the
        labels, if any, under 'labels'.
    transform : Transform object, optional (default None)
        Transform to apply to a sample before returning it.
    """
    def __init__(self, samples, transform=None):
        self.samples = samples
        self.len = len(self.samples[next(iter(self.samples))])
        self.transform = transform

    def __len__(self):
        """
        Length of the dataset.
        """
        return self.len

    def __getitem__(self, idx):
        """
        Gets an item from the dataset.
        """
        if torch.is_tensor(idx):
            idx = idx.tolist()

        sample = {}
        for key in self.samples:
            sample[key] = self.samples[key][idx]

        if self.transform is not None:
            sample = self.transform(sample)

        return sample


################################################################################
# Transforms

class Compose:
    """
    Composes several transforms together.

    Parameters
    ----------
    transforms : Transform objects
        Transforms to combine sequentially.
    """
    def __init__(self, transforms):

        self.transforms = transforms

    def __call__(self, sample):

        for transform in self.transforms:
            sample = transform(sample)

        return sample


class SelectChannels:
    """
    Selects some particular channels in the samples.

    Parameters
    ----------
    channels : int or array-like
        Channels to output when getting an item from the dataset.
    """
    def __init__(self, channels):

        self.channels = channels

    def __call__(self, sample):

        sample['data'] = sample['data'][self.channels, ...]

        return sample


class FillNaN:
    """
    Replaces NaNs in a sample.

    Parameters
    ----------
    nan_value : float or str or array-like of shape (n_channels,), optional (default 0.)
        Value to replace NaNs in the models, which can be one value per channel
        chosen among:
            - A float to replace the NaNs directly;
            - The keyword `forward` to fill the NaN values forward along a given
              axis `forward_axis`;
            - The keyword `max` to fill the NaN values with the maximal non-NaN
              value;
            - The keyword `max+1` to fill the NaN values with the maximal non-NaN
              value plus one.
    axis : int, optional (default 0)
        Axis for the channels.
    forward_axis : int, optional (default None)
        Axis for forward-filling if `nan_value` is `forward`.
    """
    def __init__(self, nan_value=0., axis=0, forward_axis=None):

        self.nan_value = nan_value
        self.axis = axis
        self.forward_axis = forward_axis

    def _fill(self, sample, nan_value):
        """
        Fills the data of a sample.
        """
        if isinstance(nan_value, (int, float)):
            sample[np.isnan(sample)] = nan_value
        elif nan_value == 'max':
            sample[np.isnan(sample)] = np.nanmax(sample)
        elif nan_value == 'max+1':
            sample[np.isnan(sample)] = np.nanmax(sample) + 1
        elif nan_value == 'forward':
            sample = push(sample, axis=self.forward_axis)

        return sample

    def __call__(self, sample):

        if isinstance(self.nan_value, (tuple, list)):
            slices = [slice(None)]*sample['data'].ndim
            for i in range(sample['data'].shape[self.axis]):
                slices[self.axis] = slice(i, i + 1)
                sample['data'][tuple(slices)] = self._fill(sample['data'][tuple(slices)],
                                                           self.nan_value[i])
        else:
            sample['data'] = self._fill(sample['data'], self.nan_value)

        return sample


class Crop:
    """
    Crops the samples.

    Parameters
    ----------
    extent : array-like
        Extent of the cropping along each axis.
    """
    def __init__(self, extent):

        self.extent = extent

    def __call__(self, sample):

        slices = []
        for size, bounds in zip(sample['data'].shape, self.extent):
            if bounds is not None and size > 1:
                slices.append(slice(bounds[0], bounds[1]))
            else:
                slices.append(slice(None))
        sample['data'] = sample['data'][tuple(slices)]

        return sample


class RandomCrop:
    """
    Randomly crops the samples.

    Parameters
    ----------
    output_shape : array-like
        Size of the output samples along each axis.
    use_selective_crop : bool, optional (default False)
        If True, adds a selection process to the random crop to eliminate
        cropped samples with too few coarse deposits.
    channel : int, optional (default None)
        Index of the channel to use for selective random crop. If None, all the
        channels are used.
    n_attempts : int, optional (default 1000)
        Maximal number of attempts to find a suitable selective crop.
    """
    def __init__(self,
                 output_shape,
                 use_selective_crop=False,
                 channel=None,
                 n_attempts=1e5):

        self.output_shape = output_shape
        self.use_selective_crop = use_selective_crop
        self.channel = channel
        self.n_attempts = n_attempts

    def _random_crop(self, sample):
        """
        Randomly crops a sample.
        """
        slices = []
        for size, output_size in zip(sample['data'].shape, self.output_shape):
            if output_size is not None and size > 1:
                offset = torch.randint(0, size - output_size, (1,)).item() if size - output_size > 0 else 0
                slices.append(slice(offset, offset + output_size))
            else:
                slices.append(slice(None))
        sample['data'] = sample['data'][tuple(slices)]

        return sample

    def _selective_random_crop(self, sample):
        """
        Randomly crops a sample while eliminating cropping with almost no
        coarse deposits.
        """
        threshold = np.nanmedian(np.nanmean(sample['data'][self.channel], axis=-1))
        value = 0.
        attempt = 0
        while value <= threshold and attempt < self.n_attempts:
            subsample = self._random_crop(sample)
            value = np.nanmedian(np.nanmean(subsample['data'][self.channel], axis=-1))
            attempt += 1

        return subsample

    def __call__(self, sample):

        if self.use_selective_crop:
            return self._selective_random_crop(sample)
        else:
            return self._random_crop(sample)


class Scale:
    """
    Scales a sample between -1 and 1.

    Parameters
    ----------
    channel_bounds : array-like, optional (default None)
        Minimum and maximum values for each channel to use during scaling.
    """
    def __init__(self, channel_bounds=None):

        self.channel_bounds = channel_bounds

    def __call__(self, sample):

        if self.channel_bounds is None:
            a = 2./np.ptp(sample['data'], axis=(1, 2, 3), keepdims=True)
            b = 1. - a*np.max(sample['data'], axis=(1, 2, 3), keepdims=True)
            sample['data'] = a*sample['data'] + b
        else:
            for c, bounds in enumerate(self.channel_bounds):
                if bounds is None:
                    a = 2./np.ptp(sample['data'][c])
                    b = 1. - a*np.max(sample['data'][c])
                    sample['data'][c] = a*sample['data'][c] + b
                else:
                    a = 2./(bounds[1] - bounds[0])
                    b = 1. - a*bounds[1]
                    sample['data'][c] = a*sample['data'][c] + b

        return sample


class ToTensor:
    """
    Converts NumPy's ndarrays to PyTorch's tensors.

    Parameters
    ----------
    dtype : NumPy dtype, optional (default float32)
        Type of the output sample.
    reorder : bool, optional (default False)
        If True, changes the sample order from (Z,H,W) to (H,W,Z).
    squeeze : bool, optional (default False)
        If True, removes the axis with a single element.
    """
    def __init__(self, dtype=np.float32, reorder=False, squeeze=False):

        self.dtype = dtype
        self.reorder = reorder
        self.squeeze = squeeze

    def __call__(self, sample):

        if self.reorder == True:
            sample['data'] = np.moveaxis(sample['data'], 1, -1)
        if self.squeeze == True:
            axis = tuple(i + 1 for i, s in enumerate(sample['data'].shape[1:]) if s < 2)
            sample['data'] = sample['data'].squeeze(axis=axis)
        sample['data'] = torch.from_numpy(sample['data'].astype(self.dtype))
        if 'labels' in sample:
            sample['labels'] = torch.from_numpy(sample['labels'].astype(self.dtype))

        return sample


class Discretize:
    """
    Selects some particular channels in the samples.

    Parameters
    ----------
    bins : array-like
        Array of bins. It has to be 1-dimensional and monotonic.
    channel : int, optional (default None)
        Index of the channel to use for selective random crop. If None, all the
        channels are used.
    """
    def __init__(self, bins, channel=None):

        self.bins = bins
        self.channel = slice() if channel is None else channel

    def __call__(self, sample):

        isnot_nan = ~np.isnan(sample['data'][self.channel])
        sample['data'][self.channel][isnot_nan] = np.digitize(sample['data'][self.channel][isnot_nan],
                                                              self.bins)

        return sample


################################################################################
# Utils

def random_split(dataset, test_size=0.25):
    """
    Splits the training data into a training set and a test set.

    Parameters
    ----------
    dataset : Dataset
        PyTorch dataset giving access to the data to split.
    test_size : int or float, optional (default 0.25)
        If float, should be between 0. and 1. and represents the proportion of
        the dataset to include in the test split. If int, represents the
        absolute number of test samples.

    Returns
    -------
    datasets : Dataset
        Two PyTorch datasets, one for training and one for testing.
    """
    if test_size < 1.:
        test_size = int(test_size*len(dataset))
    training_size = len(dataset) - test_size

    return data.random_split(dataset, [training_size, test_size])


class RandLabels:
    """
    Samples some labels from a uniform distribution.

    Parameters
    ----------
    n_features : int
        Number of features in the sample vector.
    bounds : array-like of shape (2,), optional (default (-1., 1.) )
        Minimum and maximum values of the uniform distribution.
    """
    def __init__(self, n_features, bounds=(-1., 1.)):

        self.n_features = n_features
        self._sampler = Uniform(bounds[0], bounds[1])

    def __call__(self, batch_size=1):
        """
        Samples the labels.

        batch_size : int, optional (default 1)
            Number of labels per batch to sample.
        """
        return self._sampler.sample(sample_shape=(batch_size, self.n_features))
