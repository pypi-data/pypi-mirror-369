"""Datasets to handle training data from FluvDepoSet"""

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


import h5py
import numpy as np
import scipy.stats as stats
from joblib import Parallel, delayed

import torch
from torch.distributions.distribution import Distribution
from torch.distributions.normal import Normal
from torch.distributions.uniform import Uniform

from .datasets import HDF5Dataset


################################################################################
# Datasets

class FullFluvDepoSetDataset(HDF5Dataset):
    '''
    Dataset to read HDF5 files from FluvDepoSet.
    
    Parameters
    ----------
    root : str
        Path to the folder containing the hdf5 files.
    transform : Transform object, optional (default None)
        Transform to apply to a sample before returning it.
    file_paths : array-like of shape (n_files,), optional (default None)
        Paths of the samples that should be part of the dataset. If not None,
        then `root` is ignored.
    return_params : bool, optional (default True)
        If true, return the parameters of a sample with the sample.
    n_time_steps : int, optional (default None)
        Number of time steps to interpolate the time-series parameters. If None,
        no interpolation is performed and the raw parameters are returned.
    params_exclude : array-like, optional (default None)
        Parameters to exclude.
    normalize : bool, optional (default True)
        If true, normalizes the label values between -1. and 1. based on `bounds`.
    bounds : array-like of shape (n_labels, 2), optional (default None)
        Minimum and maximum values for each input parameters. Time-varying
        parameters must have two sets of bounds: one for the time steps, one for
        the actual values.
    '''
    def __init__(self,
                 root,
                 transform=None,
                 file_paths=None,
                 return_params=True,
                 n_time_steps=None,
                 params_exclude=None,
                 normalize=True,
                 bounds=None):

        super().__init__(root, transform, file_paths)
        self.return_params = return_params
        self.n_time_steps = n_time_steps
        self.params_time = ('ST_PMEAN', 'FP_INLET_ELEVATION')
        self.params_exclude = params_exclude if params_exclude is not None else []
        self.normalize = normalize
        self.bounds = self._define_bounds() if bounds is None else bounds

    def _define_bounds(self):
        """
        Defines the default bounds for each parameters.
        """
        return {'GRAINDIAM1': (0.0000625, 0.002),
                'GRAINDIAM2': (0.0000039, 0.0000625),
                'BANKERO': (0.000025, 0.0005),
                'FP_MU': (0.25, 0.5),
                'FP_LAMBDA': (750., 1500.),
                'FP_INLET_ELEVATION': ((500., 5000.), (2., 16.)),
                'ST_PMEAN': ((500., 5000.), (5., 20.))}

    def _interpolate(self, x, y, x_new, kind='linear'):
        """
        Interpolates time series labels.
        """
        if kind == 'linear':
            return np.interp(x_new, x, y)
        elif kind == 'previous':
            x_shift = np.nextafter(x, -np.inf)
            x_new_indices = np.searchsorted(x_shift, x_new, side='left')
            return y[x_new_indices - 1]

    def _normalize(self, value, bounds):
        """
        Normalizes a value between -1. and 1.
        """
        a = 2./(bounds[1] - bounds[0])
        b = 1. - a*bounds[1]

        return a*value + b

    def _get_params(self, file):
        '''
        Get the parameters of a sample.
        '''
        params = []
        for param in file['model'].attrs:
            if param not in self.params_exclude and param not in self.params_time:
                value = file['model'].attrs[param]
                if self.normalize:
                    value = self._normalize(value, self.bounds[param])
                params.append(value)
        if self.n_time_steps is None:
            for param in self.params_time:
                if param not in self.params_exclude:
                    # Time steps
                    value = file['model'].attrs[param][1:, 0] - file['model'].attrs[param][:-1, 0]
                    if self.normalize:
                        value = self._normalize(value, self.bounds[param][0])
                    params += value.tolist()
                    # Values
                    value = file['model'].attrs[param][:, 1]
                    if self.normalize:
                        value = self._normalize(value, self.bounds[param][1])
                    params += value.tolist()
        else:
            time_steps = np.linspace(file['model'].attrs[self.params_time[0]][0, 0],
                                     file['model'].attrs[self.params_time[0]][-1, 0],
                                     self.n_time_steps)
            for param in self.params_time:
                if param not in self.params_exclude:
                    # Time steps
                    value= self._interpolate(file['model'].attrs[param][:-1, 0],
                                             file['model'].attrs[param][1:, 0] - file['model'].attrs[param][:-1, 0],
                                             time_steps,
                                             kind='previous')
                    if self.normalize:
                        value = self._normalize(value, self.bounds[param][0])
                    params += value.tolist()
                    # Values
                    value = self._interpolate(file['model'].attrs[param][:, 0],
                                              file['model'].attrs[param][:, 1],
                                              time_steps,
                                              kind='linear')
                    if self.normalize:
                        value = self._normalize(value, self.bounds[param][1])
                    params += value.tolist()
            
        return np.array(params)

    def __getitem__(self, idx):
        '''
        Gets an item from the dataset.
        '''
        if torch.is_tensor(idx):
            idx = idx.tolist()

        with h5py.File(self.file_paths[idx], 'r') as file:
            sample = {'data': file['model'][:]}
            if self.return_params == True:
                sample['labels'] = self._get_params(file)
            if self.transform is not None:
                sample = self.transform(sample)

            return sample


class FluvDepoSetDataset(HDF5Dataset):
    '''
    Dataset to read HDF5 files from FluvDepoSet with basic labels.
    
    Parameters
    ----------
    root : str
        Path to the folder containing the hdf5 files.
    transform : Transform object, optional (default None)
        Transform to apply to a sample before returning it.
    file_paths : array-like of shape (n_files,), optional (default None)
        Paths of the samples that should be part of the dataset. If not None,
        then `root` is ignored.
    return_params : bool, optional (default True)
        If true, return the parameters of a sample with the sample.
    normalize : bool, optional (default True)
        If true, normalizes the label values between -1 and 1.
    n_jobs : int, optional (default 1)
        Maximum number of concurrently running jobs when fitting distributions
        to the time-dependent parameters. 
    '''
    def __init__(self,
                 root,
                 transform=None,
                 file_paths=None,
                 return_params=True,
                 normalize=True,
                 n_jobs=1):

        super().__init__(root, transform, file_paths)
        self.return_params = return_params
        self.normalize = normalize
        self.n_jobs = n_jobs
        self._bounds = {'GRAINDIAM1': (0.0000625, 0.002),
                        'GRAINDIAM2': (0.0000039, 0.0000625),
                        'BANKERO': (0.000025, 0.0005),
                        'FP_INLET_ELEVATION': ((16. - 3.6)/75000., 0.001),
                        'ST_PMEAN': (5., 20.)}
        self._dist_params = None
        if return_params == True and normalize == True:
            self._dist_params = self._fit_dist()
        
    def _mean_agg(self, file):
        """
        Computes the mean aggradation rate.
        """
        values = file['model'].attrs['FP_INLET_ELEVATION']

        return (values[-1, 1] - values[0, 1])/(values[-1, 0] - values[0, 0])
    
    def _mean_rain(self, file):
        """
        Computes the average of the mean storm rainfall.
        """
        values = file['model'].attrs['ST_PMEAN']
        time_steps = values[1:, 0] - values[:-1, 0]
        # Area bottom rectangles
        base_cum_rainfall = np.minimum(values[1:, 1], values[:-1, 1])*time_steps
        # Area top triangles
        cum_rainfall = base_cum_rainfall + time_steps*np.abs(values[1:, 1] - values[:-1, 1])/2.

        return np.sum(cum_rainfall)/values[-1, 0]
    
    def _get_mean_params(self, i):
        """
        Get the mean aggradation rate and storm rainfall.
        """
        with h5py.File(self.file_paths[i], 'r') as file:
            return self._mean_agg(file), self._mean_rain(file)
        
    def _fit_dist(self):
        """
        Fit gamma distributions to the distributions of mean aggradation rate and
        storm rainfall to be able to uniformize them.
        """
        params = Parallel(n_jobs=self.n_jobs)(delayed(self._get_mean_params)(i) for i in range(self.len))
        params = np.array(params)
        
        return [stats.gamma.fit(1000.*params[:, 0]), stats.gamma.fit(params[:, 1])]

    def _normalize(self, value, bounds):
        """
        Normalizes a value between -1. and 1.
        """
        a = 2./(bounds[1] - bounds[0])
        b = 1. - a*bounds[1]

        return a*value + b

    def _get(self, file, param):
        """
        Gets a parameter value.
        """
        value = file['model'].attrs[param]
        if self.normalize:
            value = self._normalize(value, self._bounds[param])

        return value

    def _get_agg(self, file):
        """
        Gets the mean aggradation rate.
        """
        value = self._mean_agg(file)
        if self.normalize:
            value = 2.*stats.gamma.cdf(1000.*value, *self._dist_params[0]) - 1.

        return value
    
    def _get_rain(self, file):
        """
        Gets the average of the mean storm rainfall.
        """
        value = self._mean_rain(file)
        if self.normalize:
            value = 2.*stats.gamma.cdf(value, *self._dist_params[1]) - 1.

        return value

    def _get_params(self, file):
        '''
        Get the parameters of a sample.
        '''
        params = [self._get(file, 'GRAINDIAM1'),
                  self._get(file, 'GRAINDIAM2'),
                  self._get(file, 'BANKERO'),
                  self._get_agg(file),
                  self._get_rain(file)]
        # params = [self._get(file, 'BANKERO'),
        #           self._get_agg(file)]

        return np.array(params)

    def __getitem__(self, idx):
        '''
        Gets an item from the dataset.
        '''
        if torch.is_tensor(idx):
            idx = idx.tolist()

        with h5py.File(self.file_paths[idx], 'r') as file:
            sample = {'data': file['model'][:]}
            if self.return_params == True:
                sample['labels'] = self._get_params(file)
            if self.transform is not None:
                sample = self.transform(sample)

            return sample


################################################################################
# Random labels

class RandTimeSeries:
    """
    Generates random time series to define CHILD's time series parameters. Not
    all parameters are meant to work together, e.g., value and rate are mutually
    exclusive. Not all configurations were thoroughly tested, so make sure to
    test that it does what you want before using this.
    
    Parameters
    ----------
    initial_time : float
        Initial time of the time series.
    time_steps : float or scipy.stats' rv_continuous
        Time steps for the variations of the time series.
    final_time : float, optional (default None)
        Final time of the time series.
    max_final_time : float, optional (default None)
        Maximum final time of the time series.
    initial_value : float, optional (default None)
        Initial value of the time series.
    rate : float or scipy.stats' rv_continuous, optional (default None)
        Rate of variation of the time series.
    final_value : float, optional (default None)
        Final value of the time series.
    minimal_value : float, optional (default None)
        Minimal value of the time series.
    value : float or scipy.stats' rv_continuous, optional (default None)
        Value of the time series.
    autocorr : float, optional (default None)
        Autocorrelation of the time series.
    """
    def __init__(self,
                 initial_time,
                 time_steps,
                 final_time=None,
                 max_final_time=None,
                 initial_value=None,
                 rate=None,
                 final_value=None,
                 minimal_value=None,
                 value=None,
                 autocorr=None):

        if (value is None and (rate is None or initial_value is None)):
            raise ValueError("Invalid parameters: either use value, or rate with an initial value")

        self.initial_time = initial_time
        self.time_steps = time_steps
        self.final_time = final_time
        self.rate = rate
        self.initial_value = initial_value
        self.final_value = final_value
        self.max_final_time = max_final_time
        self.minimal_value = minimal_value
        self.value = value
        self.autocorr = autocorr

    def _sample(self, input):
        """
        Samples from an input if it's a distribution.
        """
        if isinstance(input, Distribution) == True:
            return input.sample()
        return input

    def sample(self, final_time=None, max_iter=1e8):
        """
        Samples a time series.

        final_time : float, optional (default None)
            Final time of the time series. Used to fit the final time of another
            time series.
        max_iter : float, optional (default 1e8)
            Maximal number of iterations to fit the last value or last time.
        """
        if final_time is None:
            final_time = self.final_time
        max_final_time = self.max_final_time if self.max_final_time is not None else float('inf')

        times = [float('inf')]
        values = [float('nan')]
        C = None
        if self.autocorr is not None:
            C = torch.linalg.cholesky(torch.Tensor([[1., 0.], [self.autocorr, 1.]]),
                                      upper=False)
        
        iter_count = 0
        while (((values[-1] != self.final_value and times[-1] != final_time)
                or times[-1] > max_final_time
                or (self.minimal_value is not None
                    and any(x < self.minimal_value for x in values) == True))
               and iter_count < max_iter):

            times = [self.initial_time]
            initial_value = None
            previous_value = None
            if self.initial_value is None:
                initial_value = self._sample(self.value)
                previous_value = self.value.cdf(initial_value)
                previous_value = Normal(0., 1.).icdf(previous_value)
            else:
                initial_value = self._sample(self.initial_value)
            values = [initial_value]
            while (values[-1] != self.final_value
                   and times[-1] != final_time
                   and times[-1] < max_final_time):

                time_step = self._sample(self.time_steps)
                new_time = times[-1] + time_step
                
                new_value = None
                if self.rate is not None:
                    rate = self._sample(self.rate)
                    if final_time is not None:
                        if new_time > final_time:
                            new_time = final_time
                            time_step = new_time - times[-1]
                        new_value = values[-1] + rate*time_step
                    elif self.final_value is not None:
                        new_value = values[-1] + rate*time_step
                        if new_value > self.final_value:
                            rate = (self.final_value - times[-1])/(new_value - times[-1])
                            new_time = torch.round(times[-1] + rate*time_step)
                            new_value = self.final_value
                else:
                    new_value = self._sample(Normal(0., 1.))
                    if C is not None:
                        new_value = torch.matmul(C, torch.Tensor([previous_value, new_value]))[1]
                        previous_value = new_value
                    new_value = Normal(0., 1.).cdf(new_value)
                    new_value = self.value.icdf(new_value)
                    if (new_time > final_time):
                        new_value = values[-1] + (new_value - values[-1])*(final_time - times[-1])/(new_time - times[-1])
                        new_time = final_time

                times.append(new_time)
                values.append(new_value)

            iter_count += 1

        return torch.Tensor([times, values])


class RandFluvDepoSetLabels:

    def __init__(self,
                 bank_erodibility=None,
                 fp_lambda=None,
                 fp_mu=None,
                 coarse_diameter=None,
                 fine_diameter=None,
                 inlet_elevation=None,
                 mean_storm_rainfall=None,
                 n_time_steps=100):
        """
        Generates random labels similar to those of the FluvDepoSet dataset.

        bank_erodibility : float or PyTorch Distribution, optional (default None)
            Bank erodibility. By default, the distribution used to generate the
            FluvDepoSet dataset.
        fp_lambda : float or PyTorch Distribution, optional (default None)
            Overbank distance decay constant. By default, the distribution used
            to generate the FluvDepoSet dataset.
        fp_mu : float or PyTorch Distribution, optional (default None)
            Overbank deposition rate constant. By default, the distribution used
            to generate the FluvDepoSet dataset.
        coarse_diameter : float or PyTorch Distribution, optional (default None)
            Coarse grain diameter. By default, the distribution used to generate
            the FluvDepoSet dataset.
        fine_diameter : float or PyTorch Distribution, optional (default None)
            Fine grain diameter. By default, the distribution used to generate
            the FluvDepoSet dataset.
        inlet_elevation : RandTimeSeries, optional (default None)
            River inlet elevation. By default, the distribution used to generate
            the FluvDepoSet dataset.
        mean_storm_rainfall : RandTimeSeries, optional (default None)
            Mean storm rainfall. By default, the distribution used to generate
            the FluvDepoSet dataset.
        n_time_steps : int, optional (default 100)
            Number of time steps to use when resampling the time series.
        """
        self.bank_erodibility = bank_erodibility if bank_erodibility is not None else Uniform(0.000025, 0.0005)
        self.fp_lambda = fp_lambda if fp_lambda is not None else Uniform(750., 1500.)
        self.fp_mu = fp_mu if fp_mu is not None else Uniform(0.25, 0.5)
        self.coarse_diameter = coarse_diameter if coarse_diameter is not None else Uniform(0.0000625, 0.002)
        self.fine_diameter = fine_diameter if fine_diameter is not None else Uniform(0.0000039, 0.0000625)
        self.inlet_elevation = inlet_elevation if inlet_elevation is not None else RandTimeSeries(0.,
                                                                                                  Uniform(500., 5000.),
                                                                                                  max_final_time=75000.,
                                                                                                  initial_value=3.6,
                                                                                                  minimal_value=2.,
                                                                                                  rate=Uniform(-1e-3, 1e-3),
                                                                                                  final_value=16)
        self.mean_storm_rainfall = mean_storm_rainfall if mean_storm_rainfall is not None else RandTimeSeries(0.,
                                                                                                              Uniform(500., 5000.),
                                                                                                              value=Uniform(5., 20.),
                                                                                                              autocorr=0.75)
        self.n_time_steps = n_time_steps

    def _sample(self, input, sample_shape=torch.Size([])):
        """
        Samples from an input if it's a distribution.
        """
        if isinstance(input, Distribution) == True:
            return input.sample(sample_shape=sample_shape)
        return input

    # def _interpolate(self, x, y, x_new, kind='linear'):
    #     """
    #     Interpolates time series labels.
    #     """
    #     interpolator = interp1d(x, y, kind=kind, fill_value='extrapolate')

    #     return interpolator(x_new).tolist()

    def _interpolate(self, x, y, x_new, kind='linear'):
        """
        Interpolates time series labels.
        """
        if kind == 'linear':
            return torch.Tensor(np.interp(x_new, x, y))
        elif kind == 'previous':
            x_shift = torch.nextafter(x, torch.full(x.shape, -float('inf')))
            x_new_indices = torch.searchsorted(x_shift, x_new, right=False)
            return y[x_new_indices - 1]

    def __call__(self, batch_size=1):
        """
        Samples the labels.

        batch_size : int, optional (default 1)
            Number of labels per batch to sample.
        """
        labels = [self._sample(self.bank_erodibility, torch.Size([batch_size, 1])),
                  self._sample(self.fp_lambda, torch.Size([batch_size, 1])),
                  self._sample(self.fp_mu, torch.Size([batch_size, 1])),
                  self._sample(self.coarse_diameter, torch.Size([batch_size, 1])),
                  self._sample(self.fine_diameter, torch.Size([batch_size, 1]))]

        time_rainfalls = torch.empty(batch_size, self.n_time_steps)
        rainfalls = torch.empty(batch_size, self.n_time_steps)
        time_elevations = torch.empty(batch_size, self.n_time_steps)
        elevations = torch.empty(batch_size, self.n_time_steps)
        for b in range(batch_size):
            elevation = self.inlet_elevation.sample()
            rainfall = self.mean_storm_rainfall.sample(final_time=elevation[0, -1])

            times = torch.linspace(elevation[0, 0], elevation[0, -1], self.n_time_steps)
            time_rainfalls[b] = self._interpolate(rainfall[0, :-1],
                                                  rainfall[0, 1:] - rainfall[0, :-1],
                                                  times,
                                                  kind='previous')
            rainfalls[b] = self._interpolate(rainfall[0],
                                             rainfall[1],
                                             times,
                                             kind='linear')
            time_elevations[b] = self._interpolate(elevation[0, :-1],
                                                   elevation[0, 1:] - elevation[0, :-1],
                                                   times,
                                                   kind='previous')
            elevations[b] = self._interpolate(elevation[0],
                                              elevation[1],
                                              times,
                                              kind='linear')

        labels += [time_rainfalls, rainfalls, time_elevations, elevations]

        return torch.cat(labels, axis=-1)
