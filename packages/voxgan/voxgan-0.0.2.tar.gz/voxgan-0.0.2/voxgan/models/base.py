"""Generative Adversarial Network"""

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


import os
import inspect
from functools import partial
import time
from datetime import timedelta
from pathlib import Path
from collections import defaultdict
from contextlib import nullcontext
import csv
import h5py

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import torch.distributed as dist
from torch.utils.data.distributed import DistributedSampler
from torch.nn.parallel import DistributedDataParallel as DDP
from torch.distributed.optim import ZeroRedundancyOptimizer
import torch.multiprocessing as mp
from torch.cuda.amp import autocast
from torch.cuda.amp import GradScaler

from ..data.datasets import random_split
from ..networks.utils import initialize_weights_normal
from ..networks.utils import EMA


################################################################################
# Utils

def isinstancialized(object):
    """
    Check whether an object is an instancialized class.

    Parameters
    ----------
    object : object
        An object that is can be a class or an instance of a class.
    
    Returns
    -------
    is_instancialized : bool
        True if `object` is a class, false otherwise.
    """
    if inspect.isclass(object) == True or isinstance(object, partial) == True:
        return False
    else:
        return True


################################################################################
# Tensor distribution

def move_to(input, device, non_blocking=False):
    """
    Moves an input to a device (e.g., a GPU).

    Parameters
    ----------
    input : Tensor
        PyTorch tensor.
    device : Device
        PyTorch device to move the tensor to.
    non_blocking : bool, optional (default False)
        If True, try to convert asynchronously with respect to the host if
        possible.
    """
    if torch.is_tensor(input):
        return input.to(device, non_blocking=non_blocking)
    elif isinstance(input, dict):
        output = {}
        for key, value in input.items():
            output[key] = move_to(value, device, non_blocking)
        return output
    elif isinstance(input, list):
        output = []
        for value in input:
            output.append(move_to(value, device, non_blocking))
        return output
    else:
        raise TypeError('Cannot move input to the device: Invalid input type.')


def move_to_cpu(input):
    """
    Moves an input to CPU.

    Parameters
    ----------
    input : Tensor
        PyTorch tensor.
    """
    if torch.is_tensor(input):
        return input.cpu()
    elif isinstance(input, dict):
        output = {}
        for key, value in input.items():
            output[key] = move_to_cpu(value)
        return output
    elif isinstance(input, list):
        output = []
        for value in input:
            output.append(move_to_cpu(value))
        return output
    else:
        raise TypeError('Cannot move input to CPU: Invalid input type.')


def detach(input):
    """
    Detaches an input from the computational graph.

    Parameters
    ----------
    input : Tensor
        PyTorch tensor.
    """
    if torch.is_tensor(input):
        return input.detach()
    elif isinstance(input, dict):
        output = {}
        for key, value in input.items():
            output[key] = detach(value)
        return output
    elif isinstance(input, list):
        output = []
        for value in input:
            output.append(detach(value))
        return output
    else:
        raise TypeError('Cannot detach input: Invalid input type.')


def copy(input):
    """
    Copies an input.

    Parameters
    ----------
    input : Tensor
        PyTorch tensor.
    """
    if torch.is_tensor(input):
        return input.detach().clone()
    elif isinstance(input, dict):
        output = {}
        for key, value in input.items():
            output[key] = copy(value)
        return output
    elif isinstance(input, list):
        output = []
        for value in input:
            output.append(copy(value))
        return output
    else:
        raise TypeError('Cannot copy input: Invalid input type.')


################################################################################
# Training

class BaseTrainer:
    """
    Base class for training processes.
    
    Parameters
    ----------
    output_dir_path : str, optional (default '.')
        Path to the directory in which checkpoints and samples are saved.
    output_label : str, optional (default 'CNN')
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
    history_ : defaultdict
        Store the training history, e.g., epoch, batch number, losses, metrics.
    """
    def __init__(self,
                 output_dir_path='.',
                 output_label='CNN',
                 verbose=1,
                 num_gpus=1,
                 num_nodes=1,
                 distributed=False,
                 backend='gloo',
                 use_amp_training=False):

        self.output_dir_path = Path(output_dir_path)
        self.output_dir_path.mkdir(parents=True, exist_ok=True)
        self.output_label = output_label
        self.verbose = verbose
        self.num_gpus = num_gpus
        self.num_nodes = num_nodes
        self._master_device = torch.device('cuda:0' if (torch.cuda.is_available() and num_gpus > 0) else 'cpu')
        self.distributed = distributed #if torch.distributed.is_available() == True else False
        self.backend = backend
        self.use_amp_training = use_amp_training

        self.history_ = None

    def _load_data(self,
                   dataset,
                   batch_size=128,
                   shuffle=True,
                   validation_set=None,
                   validation_size=0.1,
                   validation_batch_size=128,
                   preload_validation=False,
                   metrics=None,
                   num_workers=1,
                   pin_memory=False,
                   drop_last=False,
                   device=None,
                   seed=42):
        """
        Splits the data between a training and validation set if needed and
        creates the data loaders.

        Parameters
        ----------
        dataset : Dataset
            PyTorch dataset giving access to the data for training.
        batch_size : int, optional (default 128)
            Number of samples per batch to load.
        shuffle : bool, optional (default True)
            If True, shuffle the data when loading, otherwise preserve their
            original order.
        metrics : tuple or list, optional (default None)
            List of metric objects to compare samples from the generator with
            a validation set.
        validation_set : Dataset, optional (default None)
            PyTorch dataset giving access to the data for validation. If None,
            will be extracted from `dataset`.
        validation_size : float, optional (default 0.1)
            Proportion of the training data to set aside for validation with the
            metrics.
        validation_batch_size : int, optional (default 128)
            Number of samples per batch to load during validation.
        preload_validation : bool, optional (default False)
            If True, loads the validation samples once at the beginning of
            training instead of at each validation step. Makes training faster
            but leads to a higher memory burden.
        num_workers : int, optional (default 1)
            Number of subprocesses to use for data loading. 0 means that the
            data will be loaded in the main process.
        pin_memory : bool, optional (default False)
            If `True`, the data loader will copy Tensors into CUDA pinned memory
            before returning them
        drop_last : bool, optional (default False)
            If `True`, drop the last incomplete batch if the dataset size is not
            divisible by the batch size.
        device : Device, optional (default None)
            PyTorch device to determine the rank in the distributed sampler,
            if used.
        seed : int, optional (default 42)
            Random seed used to shuffle the distributed sampler, if used.
        """
        if metrics is not None and (validation_set is not None or validation_size > 0.):
            if validation_set is not None:
                training_set = dataset
            else:
                training_set, validation_set = random_split(dataset, validation_size)
            sampler = None
            if self.num_gpus > 1 and self.distributed == True:
                sampler = DistributedSampler(training_set,
                                             num_replicas=self.num_nodes*self.num_gpus,
                                             rank=device,
                                             shuffle=shuffle,
                                             seed=seed,
                                             drop_last=drop_last)
                shuffle = False
            training_loader = DataLoader(training_set,
                                         batch_size=batch_size,
                                         shuffle=shuffle,
                                         sampler=sampler,
                                         num_workers=num_workers,
                                         pin_memory=pin_memory,
                                         drop_last=drop_last)
            if preload_validation == True:
                validation_batch_size = len(validation_set)
            validation_loader = DataLoader(validation_set,
                                           batch_size=validation_batch_size,
                                           shuffle=False,
                                           num_workers=num_workers,
                                           pin_memory=pin_memory)
        else:
            sampler = None
            if self.num_gpus > 1 and self.distributed == True:
                sampler = DistributedSampler(dataset,
                                             num_replicas=self.num_nodes*self.num_gpus,
                                             rank=device,
                                             shuffle=shuffle,
                                             seed=seed,
                                             drop_last=drop_last)
                shuffle = False
            training_loader = DataLoader(dataset,
                                         batch_size=batch_size,
                                         shuffle=shuffle,
                                         sampler=sampler,
                                         num_workers=num_workers,
                                         pin_memory=pin_memory,
                                         drop_last=drop_last)
            validation_loader = None

        return training_loader, validation_loader

    def save_checkpoint(self, checkpoint_id=None):
        """
        Saves a checkpoint during training.
        
        Parameters
        ----------
        checkpoint_id : str, optional (default None)
            ID to differentiate the file name from the previous training
            checkpoints.
        """
        checkpoint_id = '_' + checkpoint_id if checkpoint_id is not None else ''

        checkpoint_dir = self.output_dir_path/(self.output_label + '_Training_Checkpoints')
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        checkpoint_file = checkpoint_dir/(self.output_label + '_training_checkpoint' + checkpoint_id + '.pt')
        self.save(checkpoint_file, training=True)

    def load_checkpoint(self, checkpoint_id, map_location=None, rank=0):
        """
        Loads a checkpoint to resume training.
        
        Parameters
        ----------
        checkpoint_id : str
            ID of the training checkpoint to load.
        map_location : torch.device or dict (default None)
            Specifies how to remap storage locations.
        rank : int (default 0)
            Rank of the process.
        """
        checkpoint_dir = self.output_dir_path/(self.output_label + '_Training_Checkpoints')
        checkpoint_file = checkpoint_dir/(self.output_label + '_training_checkpoint_' + checkpoint_id + '.pt')
        self.load(checkpoint_file, map_location, rank, training=True)

    def save_history(self, history=None, file_name='history.csv'):
        """
        Saves a training history in a csv file.
        
        Parameters
        ----------
        history : dict, optional (default None)
            Training history to save.
        file_name : str, optional (default 'history.csv')
            Name of the csv file.
        """
        if history is None:
            history = self.history_

        file_path = self.output_dir_path/(self.output_label + '_' + file_name)
        with open(file_path, 'w') as file:
            writer = csv.writer(file)
            writer.writerow(history.keys())
            writer.writerows(zip(*history.values()))

    def _setup(self, rank, world_size):
        """
        Sets up process groups for distributed training.
        """
        if 'MASTER_ADDR' not in os.environ:
            os.environ['MASTER_ADDR'] = 'localhost'
        os.environ['MASTER_PORT'] = '12355'

        # Initialize the process group
        dist.init_process_group(self.backend, rank=rank, world_size=world_size)

    def _cleanup(self):
        """
        Cleans up process groups after distributed training.
        """
        dist.destroy_process_group()

    def _init_distrib_training(self, batch_size, num_workers, device):
        """
        Initializes the parameters for distributed training.
        """
        rank = device
        if self.num_gpus > 1 and self.distributed == True:
            device = rank%self.num_gpus
            # node = (rank - device)//self.num_gpus
            self._setup(rank, self.num_nodes*self.num_gpus)

            batch_size = max(batch_size//(self.num_nodes*self.num_gpus), 1)
            num_workers = max(num_workers//(self.num_nodes*self.num_gpus), 1)

        return rank, batch_size, num_workers, device
    
    def check_main_process(self, rank):
        """
        Checks if we are in the main process.
        """
        return (self.num_gpus == 0 or
                self.distributed == False or
                (self.distributed == True and rank == 0))

    def _end_distrib_training(self):
        """
        Ends distributed training.
        """
        if self.num_gpus > 1 and self.distributed == True:
            self._cleanup()

    def _distribute_network(self, network, device):
        """
        Distributes the network(s) to the right device.
        """
        if not isinstance(network, (tuple, list)):
            network = [network]

        for i, n in enumerate(network):
            n = n.to(device)
            if self.num_gpus > 1:
                if self.distributed == True:
                    n = nn.SyncBatchNorm.convert_sync_batchnorm(n)
                    n = DDP(n, device_ids=[device])
                else:
                    n = nn.DataParallel(n)
            n.train()
            network[i] = n

        return network

    def _train(self,
               device,
               dataset,
               num_epoch,
               batch_size,
               num_accumulated,
               num_workers,
               pin_memory,
               drop_last,
               checkpoint_step,
               sampling_step,
               sampling_size,
               metrics,
               metric_step,
               validation_size,
               validation_batch_size,
               preload_validation,
               save_history,
               resume_checkpoint_id):
        """
        Trains the network on a device.
        """
        rank, batch_size, num_workers, device = self._init_distrib_training(batch_size,
                                                                            num_workers,
                                                                            device)

        raise NotImplementedError

        self._end_distrib_training()

    def train(self,
              dataset,
              num_epochs=5,
              batch_size=128,
              num_workers=1,
              pin_memory=False,
              drop_last=False,
              checkpoint_step=1000,
              sampling_step=1000,
              sampling_size=10,
              metrics=None,
              metric_step=1000,
              validation_dataset=None,
              validation_size=0.1,
              validation_batch_size=128,
              preload_validation=False,
              save_history=True,
              resume_checkpoint_id=None):
        """
        Trains the network.
        
        Parameters
        ----------
        dataset : Dataset
            PyTorch dataset giving access to the data for training. It should be
            uninitialized when using distributed parallel training.
        num_epochs : int, optional (default 5)
            Number of training epochs to run.
        batch_size : int, optional (default 128)
            Number of samples per batch to load.
        num_workers : int, optional (default 1)
            Number of subprocesses to use for data loading. 0 means that the
            data will be loaded in the main process.
        pin_memory : bool, optional (default False)
            If `True`, the data loader will copy Tensors into CUDA pinned memory
            before returning them
        drop_last : bool, optional (default False)
            If `True`, drop the last incomplete batch if the dataset size is not
            divisible by the batch size.
        checkpoint_step : int, optional (default 1000)
            Number of training iterations between checkpoints. Checkpoints save
            everything required to resume training.
        sampling_step : int, optional (default 1000)
            Number of training iterations between saves of samples from the
            generator to assess its progression during training.
        sampling_size : int, optional (default 10)
            Number of samples from the generator to save at each sampling step.
        metrics : tuple or list, optional (default None)
            List of metric objects to compare samples from the generator with
            a validation set.
        metric_step : int, optional (default 1000)
            Number of training iterations between computing the metrics to assess
            the generator's progression during training.
        validation_dataset : Dataset, optional (default None)
            PyTorch dataset giving access to the data for validation. If None,
            will be extracted from `dataset`.
        validation_size : float, optional (default 0.1)
            Proportion of the training data to set aside for validation with the
            metrics.
        validation_batch_size : int, optional (default 128)
            Number of samples per batch to load during validation.
        preload_validation : bool, optional (default False)
            If True, loads the validation samples once at the beginning of
            training instead of at each validation step. Makes training faster
            but leads to a higher memory burden.
        save_history : bool, optional (default True)
            If True, save the training history `history_` in a csv file at the
            end of training.
        resume_checkpoint_id : str, optional (default None)
            ID of a previous checkpoint to resume training.
        """
        if self.num_gpus > 1 and self.distributed == True:
            mp.spawn(self._train,
                     args=(dataset, num_epochs, batch_size, num_workers,
                           pin_memory, drop_last, checkpoint_step, sampling_step,
                           sampling_size, metrics, metric_step, validation_dataset,
                           validation_size, validation_batch_size, preload_validation,
                           save_history, resume_checkpoint_id),
                     nprocs=self.num_nodes*self.num_gpus,
                     join=True)
        else:
            self._train(self._master_device, dataset, num_epochs, batch_size,
                        num_workers, pin_memory, drop_last, checkpoint_step,
                        sampling_step, sampling_size, metrics, metric_step,
                        validation_dataset, validation_size, validation_batch_size,
                        preload_validation, save_history, resume_checkpoint_id)


################################################################################
# Generative Adversarial Network

class BaseGAN(BaseTrainer):
    """
    Base class to train Generative Adversarial Networks (GANs).
    
    Parameters
    ----------
    generator : nn.Module
        PyTorch model for the generator of the GAN. It should be uninitialized
        when using distributed parallel training.
    discriminator : nn.Module
        PyTorch model for the discriminator of the GAN. It should be uninitialized
        when using distributed parallel training.
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
    """
    def __init__(self,
                 generator,
                 discriminator,
                 rand_labels=None,
                 output_dir_path='.',
                 output_label='GAN',
                 verbose=1,
                 num_gpus=1,
                 num_nodes=1,
                 distributed=False,
                 backend='gloo',
                 use_amp_training=False):

        super(BaseGAN, self).__init__(output_dir_path, output_label, verbose,
                                      num_gpus, num_nodes, distributed, backend,
                                      use_amp_training)

        self.generator_ = generator
        self.discriminator_ = discriminator
        self.rand_labels = rand_labels
        self._nz = None
        if isinstancialized(self.generator_) == True:
            self._nz = self.generator_.nz

    def save(self, checkpoint_file, training=False):
        """
        Saves the state of the model in a checkpoint file.
        
        Parameters
        ----------
        checkpoint_file : str
            Path to the file in which the model state is to be saved.
        training : bool, optional (default False)
            If False, only the states of the generator and discriminator are 
            saved. If True, the current epoch and the optimizers' states are
            saved as well.
        """
        state = {'generator': self.generator_.state_dict(),
                 'discriminator': self.discriminator_.state_dict()}
        if self.use_ema == True:
            state['ema_model'] = self.ema_model_.state_dict()
        if training == True:
            state['epoch'] = self._epoch + 1
            state['optimizer_generator'] = self.optimizer_generator.state_dict()
            state['optimizer_discriminator'] = self.optimizer_discriminator.state_dict()
        torch.save(state, checkpoint_file)

    def load(self, checkpoint_file, map_location, rank, training=False):
        """
        Loads the state of the model from a checkpoint file.
        
        Parameters
        ----------
        checkpoint_file : str
            Path to the file in which the model state is saved.
        map_location : torch.device or dict
            Specifies how to remap storage locations.
        training : bool, optional (default False)
            If False, only the states of the generator and discriminator are 
            loaded. If True, the current epoch and the optimizers' states are
            loaded as well.
        """
        if os.path.exists(checkpoint_file):
            checkpoint = torch.load(checkpoint_file, map_location=map_location)
            self.generator_.load_state_dict(checkpoint['generator'])
            self.discriminator_.load_state_dict(checkpoint['discriminator'])
            if self.use_ema == True:
                self.ema_model_.load_state_dict(checkpoint['ema_model'])
            if training == True:
                self._epoch = checkpoint['epoch']
                self.optimizer_generator.load_state_dict(checkpoint['optimizer_generator'])
                self.optimizer_discriminator.load_state_dict(checkpoint['optimizer_discriminator'])
            if self.verbose > 0 and self.check_main_process(rank) == True:
                print("Model loaded from {}".format(checkpoint_file))
        else:
            if self.verbose > 0 and self.check_main_process(rank) == True:
                print("No checkpoint available")

    def configure(self,
                  optimizer_generator,
                  optimizer_discriminator,
                  loss_generator,
                  loss_discriminator,
                  loss_labels_generator=None,
                  loss_labels_discriminator=None,
                  initialize_weights=initialize_weights_normal,
                  num_iter_discriminator=1,
                  num_accumulated=1,
                  fake_label_generator=1.,
                  real_label_discriminator=1.,
                  fake_label_discriminator=0.,
                  clamp_bounds=None,
                  penalty_generator=None,
                  penalty_discriminator=None,
                  use_ema=False,
                  ema_decay=0.9999):
        """
        Configures the GAN for training.
        
        Parameters
        ----------
        optimizer_generator : optim.Optimizer
            Optimizer for the generator of the GAN. It should be uninitialized
            when using distributed parallel training.
        optimizer_discriminator : optim.Optimizer
            Optimizer for the discriminator of the GAN. It should be uninitialized
            when using distributed parallel training.
        loss_generator : nn.Module
            Loss criterion for the generator of the GAN.
        loss_discriminator : nn.Module
            Loss criterion for the discriminator of the GAN.
        loss_labels_generator : nn.Module, optional (default None)
            Loss criterion for the labels (if any) in the generator of the GAN.
        loss_labels_discriminator : nn.Module, optional (default None)
            Loss criterion for the labels (if any) in the discriminator of the GAN.
        num_accumulated : int, optional (default 1)
            Number of accumulated gradient steps.
        num_iter_discriminator : int, optional (default 1)
            Number of consecutive iterations of the discriminator before an 
            iteration of the generator.
        fake_label_generator : float, optional (default 1)
            Target label of the real data for the generator.
        real_label_discriminator : float, optional (default 1)
            Target label of the real data for the discriminator.
        fake_label_discriminator : float, optional (default 0)
            Target label of the fake data for the discriminator.
        clamp_bounds : float or array-like, optional (default None)
            Bounds to clamp the weights of the discriminator. If a float, the
            bounds become (-clamp_bounds, clamp_bounds) .
        penalty_generator : nn.Module or array-like of shape (n_modules), optional (default None)
            Penalty(ies) to add to the loss function of the generator.
        penalty_discriminator : nn.Module or array-like of shape (n_modules), optional (default None)
            Penalty(ies) to add to the loss function of the discriminator.
        use_ema : bool, optional (default False)
            If True, computes an exponential moving average during training on
            the generator weights.
        ema_decay : float (default 0.9999)
            Decay to apply to the generator weights during training with
            exponential moving average.
        """
        if isinstance(clamp_bounds, (int, float)):
            clamp_bounds = (-clamp_bounds, clamp_bounds)

        self.initialize_weights = initialize_weights

        self.optimizer_generator = optimizer_generator
        self.optimizer_discriminator = optimizer_discriminator

        self.loss_generator = loss_generator
        self.loss_discriminator = loss_discriminator
        self.loss_labels_generator = loss_labels_generator
        self.loss_labels_discriminator = loss_labels_discriminator
        self.penalty_generator = penalty_generator if penalty_generator is not None else []
        if isinstance(penalty_generator, nn.Module):
            self.penalty_generator = [penalty_generator]
        self.penalty_discriminator = penalty_discriminator if penalty_discriminator is not None else []
        if isinstance(penalty_discriminator, nn.Module):
            self.penalty_discriminator = [penalty_discriminator]

        self.num_iter_discriminator = num_iter_discriminator
        self.num_accumulated = num_accumulated

        # Establish convention for real and fake labels during training
        self.real_label_discriminator = real_label_discriminator
        self.fake_label_discriminator = fake_label_discriminator
        self.fake_label_generator = fake_label_generator

        self.clamp_bounds = clamp_bounds

        self.use_ema = use_ema
        self.ema_decay = ema_decay

        self._epoch = 0

    def _train_step(self, device, batch, i_total, i_acc_discriminator, i_acc_generator, save_history, rank):
        """
        Trains the GAN on a single batch by updating the discriminator followed
        by the generator.
        """
        print_dict = {}

        is_no_sync = False
        if self.num_gpus > 1 and self.distributed == True and i_acc_discriminator == self.num_accumulated:
            is_no_sync = True
        with self.discriminator_.no_sync() if is_no_sync == True else nullcontext(), self.generator_.no_sync() if is_no_sync == True else nullcontext():
            ############################
            # (1) Update D network: maximize log(D(x)) + log(1 - D(G(z)))
            ###########################
            ## Train with all-real batch
            self.discriminator_.zero_grad(set_to_none=True)
            # Format batch
            real = move_to(batch, device, non_blocking=True)
            batch_size = real['data'].size(0)
            label = torch.full((batch_size,), self.real_label_discriminator, device=device).squeeze()
            with autocast() if self.use_amp_training else nullcontext():
                # Forward pass real batch through D
                output = self.discriminator_(real)
                # Calculate loss on all-real batch
                errD_real = self.loss_discriminator(output['data'], label)
                if 'labels' in output and 'labels' in real and self.loss_labels_discriminator is not None:
                    errD_real += self.loss_labels_discriminator(output['labels'], real['labels'])
            if (self.verbose > 1 or save_history == True) and self.check_main_process(rank) == True:
                print_dict['D_x'] = output['data'].mean().item()

            ## Train with all-fake batch
            # Generate batch of latent vectors
            noise = {'data': torch.randn(batch_size, self._nz, *self.latent_shape, device=device)}
            if self.rand_labels is not None:
                noise['labels'] = self.rand_labels(batch_size).to(device, non_blocking=True)
            label = torch.full((batch_size,), self.fake_label_discriminator, device=device).squeeze()
            with autocast() if self.use_amp_training else nullcontext():
                # Generate fake image batch with G
                fake = self.generator_(noise)
                # Classify all fake batch with D
                output = self.discriminator_(detach(fake))
                # Calculate D's loss on the all-fake batch
                errD_fake = self.loss_discriminator(output['data'], label)
                if 'labels' in output and 'labels' in fake and self.loss_labels_discriminator is not None:
                    errD_fake += self.loss_labels_discriminator(output['labels'], fake['labels'])
            if (self.verbose > 1 or save_history == True) and self.check_main_process(rank) == True:
                print_dict['D_G_z1'] = output['data'].mean().item()
            # Add the gradients from the all-real and all-fake batches
            with autocast() if self.use_amp_training else nullcontext():
                errD = errD_real + errD_fake
            for penalty in self.penalty_discriminator:
                if penalty.to_backprop == True and i_total%penalty.num_iter == penalty.num_iter - 1:
                    errP = penalty(self.discriminator_, device, real, fake, self.scaler)
                    with autocast() if self.use_amp_training else nullcontext():
                        errD += errP
            with autocast() if self.use_amp_training else nullcontext():
                errD /= self.num_accumulated
            # Calculate the gradients for this batch
            if self.use_amp_training and self.scaler is not None:
                self.scaler.scale(errD).backward(retain_graph=True)
            else:
                errD.backward(retain_graph=True)
            for penalty in self.penalty_discriminator:
                if penalty.to_backprop == False and i_total%penalty.num_iter == penalty.num_iter - 1:
                    penalty(self.discriminator_, device, real, fake, self.scaler)
            if self.clamp_bounds is not None:
                if self.use_amp_training and self.scaler is not None:
                    self.scaler.unscale_(self.optimizer_discriminator)
                # clamp parameters to a cube
                for p in self.discriminator_.parameters():
                    p.data.clamp_(*self.clamp_bounds)
            # Update D
            i_acc_discriminator += 1
            if i_acc_discriminator == self.num_accumulated:
                if self.use_amp_training and self.scaler is not None:
                    self.scaler.step(self.optimizer_discriminator)
                    if (self.num_iter_discriminator > 1 and
                        i_total%self.num_iter_discriminator != self.num_iter_discriminator - 1):
                        self.scaler.update()
                else:
                    self.optimizer_discriminator.step()
                i_acc_discriminator = 0
            # Save history
            if save_history == True and self.check_main_process(rank) == True:
                self.history_['update'].append(i_total%self.num_iter_discriminator + 1)
                self.history_['loss_discriminator'].append(errD.item())
                self.history_['D(x)'].append(print_dict['D_x'])

            ############################
            # (2) Update G network: maximize log(D(G(z)))
            ###########################
            if i_total%self.num_iter_discriminator == self.num_iter_discriminator - 1:
                self.generator_.zero_grad(set_to_none=True)
                label.fill_(self.fake_label_generator)  # fake labels are real for generator cost
                with autocast() if self.use_amp_training else nullcontext():
                    # Since we just updated D, perform another forward pass of all-fake batch through D
                    output = self.discriminator_(fake)
                    # Calculate G's loss based on this output
                    errG = self.loss_generator(output['data'], label)
                    if 'labels' in output and 'labels' in fake and self.loss_labels_generator is not None:
                        errG += self.loss_labels_generator(output['labels'], fake['labels'])
                for penalty in self.penalty_generator:
                    if penalty.to_backprop == True and i_total%penalty.num_iter == penalty.num_iter - 1:
                        errP = penalty(self.generator_, device, real, fake, self.scaler)
                        with autocast() if self.use_amp_training else nullcontext():
                            errG += errP
                with autocast() if self.use_amp_training else nullcontext():
                    errG /= self.num_accumulated
                # Calculate gradients for G
                if self.use_amp_training and self.scaler is not None:
                    self.scaler.scale(errG).backward()
                else:
                    errG.backward()
                for penalty in self.penalty_generator:
                    if penalty.to_backprop == False and i_total%penalty.num_iter == penalty.num_iter - 1:
                        penalty(self.generator_, device, real, fake, self.scaler)
                if (self.verbose > 1 or save_history == True) and self.check_main_process(rank) == True:
                    print_dict['D_G_z2'] = output['data'].mean().item()
                # Update G
                i_acc_generator += 1
                if i_acc_generator == self.num_accumulated:
                    if self.use_amp_training and self.scaler is not None:
                        self.scaler.step(self.optimizer_generator)
                        self.scaler.update()
                    else:
                        self.optimizer_generator.step()
                    if self.use_ema == True:
                        self.ema_model_.update_parameters(self.generator_)
                    i_acc_generator = 0
                # Output training stats
                if self.verbose > 1 and self.check_main_process(rank) == True:
                    print("... ... Loss_D: %.4f | Loss_G: %.4f | D(x): %.4f | D(G(z)): %.4f -> %.4f"
                        %(errD.item(), errG.item(), print_dict['D_x'], print_dict['D_G_z1'], print_dict['D_G_z2']))
                # Save history
                if save_history == True and self.check_main_process(rank) == True:
                    self.history_['loss_generator'].append(errG.item())
                    self.history_['D(G(z))'].append(print_dict['D_G_z1'])
                    self.history_['D_up(G(z))'].append(print_dict['D_G_z2'])
            elif save_history == True and self.check_main_process(rank) == True:
                self.history_['loss_generator'].append('')
                self.history_['D(G(z))'].append('')
                self.history_['D_up(G(z))'].append('')

        return i_acc_discriminator, i_acc_generator

    def _check_step(self, action_step, i_total, i_batch, num_epochs, num_batches):
        """
        Checks when to do an action during training.
        """
        i = i_total//self.num_iter_discriminator
        if ((i%action_step == 0 and i_total%self.num_iter_discriminator == self.num_iter_discriminator - 1) or
            (self._epoch == num_epochs - 1 and i_batch == num_batches - 1)):
            return True
        else:
            return False

    def _checkpoint(self, i_batch, i_total, num_epochs, num_batches, checkpoint_step, save_history, rank):
        """
        Saves a checkpoint.
        """
        if self._check_step(checkpoint_step, i_total, i_batch, num_epochs, num_batches):
            if self.num_gpus > 1 and self.distributed == True:
                self.optimizer_generator.consolidate_state_dict()
                self.optimizer_discriminator.consolidate_state_dict()
            if self.check_main_process(rank) == True:
                self.save_checkpoint(checkpoint_id='iteration_' + str(i_total//self.num_iter_discriminator + 1))
                if save_history == True:
                    self.history_['checkpoint'].append(True)
        elif save_history == True:
            self.history_['checkpoint'].append(False)

    def _validate(self, validation_loader, metrics, i_batch, i_total, num_epochs,
                  num_batches, metric_step, save_history, rank):
        """
        Validates the samples based on a hold-out validation set.
        """
        if validation_loader is not None and save_history == True:
            if self._check_step(metric_step, i_total, i_batch, num_epochs, num_batches):
                if self.verbose > 1 and self.check_main_process(rank) == True:
                    print('... ... Validating', i_total//self.num_iter_discriminator + 1)
                for metric in metrics:
                    distance = metric(self.predict, validation_loader)
                    self.history_[str(metric)].append(distance)
                self.generator_.train()
            else:
                for metric in metrics:
                    self.history_[str(metric)].append('')

    def _sample(self, fixed_noise, samples_path, i_batch, i_total, num_epochs,
                num_batches, sampling_step, save_history, rank):
        """
        Samples the generator and saves the outputs.
        """
        if (self._check_step(sampling_step, i_total, i_batch, num_epochs, num_batches)
            and fixed_noise is not None):
            if self.verbose > 1 and self.check_main_process(rank) == True:
                print('... ... Saving', i_total//self.num_iter_discriminator + 1)
            with torch.no_grad():
                if self.use_ema == True:
                    generator = self.ema_model_
                else:
                    self.generator_.eval()
                    if self.num_gpus > 1 and self.distributed == True:
                        generator = self.generator_.module
                    else:
                        generator = self.generator_
                fake = detach(generator(fixed_noise))
                with h5py.File(samples_path, mode='a') as h5file:
                    h5dset = h5file.create_dataset('iteration_' + str(i_total//self.num_iter_discriminator + 1),
                                                    data=fake['data'].cpu().numpy())
                    if 'labels' in fixed_noise:
                        h5dset.attrs['labels'] = fake['labels'].cpu().numpy()
                self.generator_.train()
            if save_history == True:
                self.history_['sampling'].append(True)
        elif save_history == True:
            self.history_['sampling'].append(False)

    def _train(self,
               device,
               dataset,
               num_epochs,
               batch_size,
               num_workers,
               pin_memory,
               drop_last,
               checkpoint_step,
               sampling_step,
               sampling_size,
               metrics,
               metric_step,
               validation_dataset,
               validation_size,
               validation_batch_size,
               preload_validation,
               save_history,
               resume_checkpoint_id):
        """
        Trains the GAN on a device.
        """
        start = time.perf_counter()

        rank, self.batch_size, num_workers, device = self._init_distrib_training(batch_size,
                                                                                 num_workers,
                                                                                 device)
        if self.use_amp_training == True:
            self.scaler = GradScaler()
        else:
            self.scaler = None

        if isinstancialized(dataset) == False:
            dataset = dataset()
        if validation_dataset is not None and isinstancialized(validation_dataset) == False:
            validation_dataset = validation_dataset()
        if metrics is not None and isinstance(metrics, (tuple, list)) == False:
            metrics = [metrics]
        training_loader, validation_loader = self._load_data(dataset,
                                                             self.batch_size,
                                                             True,
                                                             validation_dataset,
                                                             validation_size,
                                                             validation_batch_size,
                                                             preload_validation,
                                                             metrics,
                                                             num_workers,
                                                             pin_memory,
                                                             drop_last,
                                                             device)

        if isinstancialized(self.generator_) == False:
            self.generator_ = self.generator_()
        if isinstancialized(self.discriminator_) == False:
            self.discriminator_ = self.discriminator_()
        if self._nz is None:
            self._nz = self.generator_.nz
        self.generator_.apply(self.initialize_weights)
        self.discriminator_.apply(self.initialize_weights)
        self.generator_, self.discriminator_ = self._distribute_network([self.generator_, self.discriminator_], device)
        self._epoch = 0
        if self.use_ema == True:
            self.ema_model_ = EMA(self.generator_, self.ema_decay, device, True)
        if resume_checkpoint_id is not None:
            map_location = {'cuda:%d' % 0: 'cuda:%d' % device} if self.num_gpus > 1 else self._master_device
            self.load_checkpoint(resume_checkpoint_id, map_location, rank)

        if isinstancialized(self.optimizer_generator) == False:
            if self.num_gpus > 1 and self.distributed == True:
                self.optimizer_generator = ZeroRedundancyOptimizer(self.generator_.parameters(),
                                                                   optimizer_class=self.optimizer_generator)
            else:
                self.optimizer_generator = self.optimizer_generator(self.generator_.parameters())
        if isinstancialized(self.optimizer_discriminator) == False:
            if self.num_gpus > 1 and self.distributed == True:
                self.optimizer_discriminator = ZeroRedundancyOptimizer(self.discriminator_.parameters(),
                                                                       optimizer_class=self.optimizer_discriminator)
            else:
                self.optimizer_discriminator = self.optimizer_discriminator(self.discriminator_.parameters())

        if isinstance(dataset[0], (tuple, list)):
            num_dims = len(dataset[0][0]['data'].shape) - 1
        else:
            num_dims = len(dataset[0]['data'].shape) - 1
        self.latent_shape = (1,)*num_dims

        # Lists to keep track of progress during training
        self.history_ = defaultdict(list)
        # Loads validation samples if required
        if (validation_loader is not None and
            preload_validation == True and
            self.check_main_process(rank) == True):
            validation_loader = next(iter(validation_loader))['data']
        # Fixed noise for generator sampling during training
        fixed_noise = None
        if self.check_main_process(rank) == True and sampling_size > 0:
            fixed_noise = {'data': torch.randn(sampling_size, self._nz, *self.latent_shape, device=device)}
            if self.rand_labels is not None:
                fixed_noise['labels'] = self.rand_labels(sampling_size).to(device, non_blocking=True)
        samples_path = self.output_dir_path/(self.output_label + '_training_samples.h5')
        if (resume_checkpoint_id is None and
            samples_path.exists() == True and
            (self.num_gpus < 2 or self.distributed == False or rank == 0)):
            samples_path.unlink()

        if self.verbose > 0 and self.check_main_process(rank) == True:
            print("Starting training...")

        # For each epoch
        num_batches = len(training_loader)
        i_total = 0
        i_acc_discriminator = 0
        i_acc_generator = 0
        for self._epoch in range(self._epoch, num_epochs):
            start_epoch = time.perf_counter()

            if self.num_gpus > 1 and self.distributed == True:
                training_loader.sampler.set_epoch(self._epoch)

            if self.verbose > 0 and self.check_main_process(rank) == True:
                print("... Epoch ", self._epoch + 1, "/", num_epochs, "...", sep='')

            # For each batch in the dataloader
            for i_batch, batch in enumerate(training_loader):

                if self.verbose > 1 and self.check_main_process(rank) == True:
                    print("... ... Batch ", i_batch + 1, "/", num_batches, sep='')
                if save_history == True and self.check_main_process(rank) == True:
                    self.history_['epoch'].append(self._epoch + 1)
                    self.history_['batch'].append(i_batch + 1)
                    self.history_['iteration'].append(i_total//self.num_iter_discriminator + 1)

                i_acc_discriminator, i_acc_generator = self._train_step(device, batch, i_total, i_acc_discriminator,
                                                                        i_acc_generator, save_history, rank)

                self._checkpoint(i_batch, i_total, num_epochs, num_batches, checkpoint_step, save_history, rank)
                if self.check_main_process(rank) == True:
                    self._validate(validation_loader, metrics, i_batch, i_total, num_epochs, num_batches, metric_step, save_history, rank)
                    self._sample(fixed_noise, samples_path, i_batch, i_total, num_epochs, num_batches, sampling_step, save_history, rank)

                i_total += 1

            end_epoch = time.perf_counter()
            if self.verbose > 0 and self.check_main_process(rank) == True:
                print("... Excecution time:", timedelta(seconds=end_epoch - start_epoch))

        if save_history == True and self.check_main_process(rank) == True:
            self.save_history()

        self._end_distrib_training()

        end = time.perf_counter()
        if self.verbose > 0 and self.check_main_process(rank) == True:
            print("Ending training...")
            print("Excecution time:", timedelta(seconds=end - start))

    def predict(self, num_samples=1, batch_size=None, latent_shape=None, use_ema=None, device=None):
        """
        Simulate realizations using the generator.
        
        Parameters
        ----------
        num_samples : int, optional (default 1)
            Number of samples to generate.
        batch_size : int, optional (default None)
            Number of realizations per batch to simulate.
        latent_shape : array-like, optional (default None)
            Shape of the latent vector to simulate realizations larger than the
            training shape. 1 along each dimension by default.
        use_ema : bool, optional (default None)
            If True, uses the model from the exponential moving average for
            prediction. If None, uses the value set for training.
        device : torch.device, optional (default None)
            Device to use for predictions. By default, used `_master_device`. 

        Returns
        -------
        predictions : array, shape (num_samples, num_channels, height, width, depth)
            Realizations from the generator.
        """
        if batch_size is None:
            if hasattr(self, 'batch_size'):
                batch_size = self.batch_size
            else:
                batch_size = num_samples
        if latent_shape is None:
            latent_shape = self.latent_shape
        if self.use_ema == False or use_ema is None:
            use_ema = self.use_ema
        if device is None:
            device = self._master_device
        if use_ema == True:
            generator = self.ema_model_
        else:
            self.generator_.eval()
            if self.num_gpus > 1 and self.distributed == True:
                generator = self.generator_.module
            else:
                generator = self.generator_

        with torch.no_grad():
            predictions = {'data': []}
            if self.rand_labels is not None:
                predictions['labels'] = []
            for i in range(0, num_samples, batch_size):
                b_size = min(batch_size, num_samples - i)
                noise = {'data': torch.randn(b_size, self._nz, *latent_shape, device=device)}
                if self.rand_labels is not None:
                    noise['labels'] = self.rand_labels(b_size).to(device)
                prediction = detach(generator(noise))
                predictions['data'].append(prediction['data'])
                if self.rand_labels is not None:
                    predictions['labels'].append(prediction['labels'])
            for key in predictions:
                predictions[key] = torch.cat(predictions[key], dim=0).cpu()

            return predictions


class CustomGAN(BaseGAN):
    """
    Puppet class to train Generative Adversarial Networks (GANs) from scratch.
    """
    pass
