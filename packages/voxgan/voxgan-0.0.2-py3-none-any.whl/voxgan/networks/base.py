"""Base architectures"""

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

from .blocks import LinearBlock


################################################################################
# nD

class _BaseNetwork(nn.Module):
    """
    Base network.
    
    Parameters
    ----------
    embedding : nn.Module, optional (default None)
        Label embedding.
    ne : int, optional (default 200)
        Size of the dictionary of embeddings.
    nd : int, optional (default 128)
        Size of each embedding vector.
    squeeze : bool, optional (default True)
        If true, remove the unit dimensions of the output.
    """
    def __init__(self, embedding=None, ne=200, nd=128, squeeze=True):

        super(_BaseNetwork, self).__init__()

        if embedding is not None:
            self.ne = ne
            self.nd = nd
            self.embedding = embedding(ne, nd)
        else:
            self.ne = 0
            self.nd = 0
            self.embedding = None
        self.main = nn.Sequential()
        self.squeeze = squeeze

    def forward(self, input):

        use_dict = True
        if isinstance(input, dict) == False:
            input = {'data': input}
            use_dict = False

        output = {'data': input['data']}
        if self.embedding is not None and 'labels' in input:
            labels = self.embedding(input['labels'])
            output['data'] = torch.cat([input['data'], labels.view(input['data'].shape[0], -1, *input['data'].shape[2:])], 1)
            output['labels'] = input['labels']
        output['data'] = self.main(output['data'])
        if self.squeeze == True:
            output['data'] = output['data'].squeeze()
        if use_dict == False:
            output = output['data']

        return output


class BaseGenerator(_BaseNetwork):
    """
    Base generator.
    
    Parameters
    ----------
    nz : int, optional (default 100)
        Length of the latent vector.
    embedding : nn.Module, optional (default None)
        Label embedding.
    ne : int, optional (default 200)
        Size of the dictionary of embeddings.
    nd : int, optional (default 128)
        Size of each embedding vector.
    """
    def __init__(self, nz=100, embedding=None, ne=200, nd=128):

        super(BaseGenerator, self).__init__(embedding, ne, nd, False)

        self.nz = nz


class BaseDiscriminator(_BaseNetwork):
    """
    Base discriminator.
    
    Parameters
    ----------
    embedding : nn.Module, optional (default None)
        Label embedding.
    ne : int, optional (default 200)
        Size of the dictionary of embeddings.
    nd : int, optional (default 128)
        Size of each embedding vector.
    """
    def __init__(self, embedding=None, ne=200, nd=128):

        super(BaseDiscriminator, self).__init__(embedding, ne, nd, True)


################################################################################
# Embedding

class ContEmbedding(nn.Module):
    """
    Embedding for continuous labels.
    
    Parameters
    ----------
    ni : int
        Number of features in the input vector.
    no : int
        Number of features produced by the transformation.
    nh : int, optional (default 128)
        Number of neurons in the hidden layers.
    nl : int, optional (default 1)
        Number of hidden layers.
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
    last_activation : nn.Module (default nn.Tanh)
        Activation to apply at the very end, if any.
    num_gpus : int, optional (default 1)
        Number of GPUs available. If this is 0, code will run in CPU mode. If 
        this number is greater than 0 it will run on that number of GPUs.
    """
    def __init__(self,
                 ni,
                 no,
                 nh=128,
                 nl=1,
                 bias=True,
                 layer_normalization=None,
                 weight_normalization=None,
                 activation=None,
                 last_activation=None,
                 num_gpus=1):

        super(ContEmbedding, self).__init__()

        self.num_gpus = num_gpus

        self.main = [LinearBlock(ni,
                                 nh,
                                 bias=bias,
                                 layer_normalization=layer_normalization,
                                 weight_normalization=weight_normalization,
                                 activation=activation)]
        for l in range(nl - 1):
            self.main += [LinearBlock(nh,
                                      nh,
                                      bias=bias,
                                      layer_normalization=layer_normalization,
                                      weight_normalization=weight_normalization,
                                      activation=activation)]
        self.main += [LinearBlock(nh, no, activation=last_activation)]
        self.main = nn.Sequential(*self.main)

    def forward(self, input):

        if input.is_cuda and self.num_gpus > 1:
            output = nn.parallel.data_parallel(self.main, input, range(self.num_gpus))
        else:
            output = self.main(input)

        return output
