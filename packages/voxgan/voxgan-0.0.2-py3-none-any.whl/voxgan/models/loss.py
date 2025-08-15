"""Loss and penalty functions"""

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


from contextlib import nullcontext
import torch
import torch.nn as nn
from torch import autograd
from torch.cuda.amp import autocast


################################################################################
# Wasserstein GAN loss

class WGANLoss(nn.Module):
    """
    Creates a criterion that measures the loss of Wasserstein GAN between each
    element in the input and target.

    References
    ----------
    Arjovsky, M., Chintala, S. & Bottou, L. (2017).
        Wasserstein GAN.
        arXiv preprint arXiv:1701.07875, https://arxiv.org/abs/1701.07875
    Arjovsky, M. (2017).
        Wasserstein GAN.
        https://github.com/martinarjovsky/WassersteinGAN
    """
    def __init__(self):

        super(WGANLoss, self).__init__()
        
    def forward(self, input, target):

        return torch.mean(target*input)


class WGANGradientPenalty(nn.Module):
    """
    Calculates the gradient penalty of Wasserstein GAN.
    
    Parameters
    ----------
    gamma : float, optional (default 10.)
        Weight of the gradient penalty.
    eps : float, optional (default 1e-12)
        Epsilon to add to the norm to avoid null gradient.
    num_iter : int, optional (default 1)
        Number of iterations before applying regularization to the loss function,
        aka lazy regularization.
    use_amp : bool, optional (default False)
        If True, uses automatic mixed precision.

    References
    ----------
    Gulrajani, I., Ahmed, F., Arjovsky, M., Dumoulin, V. & Courville, A. (2017).
        Improved Training of Wasserstein GANs.
        arXiv preprint arXiv:1704.00028, https://arxiv.org/abs/1704.00028
    Gulrajani, I. (2017).
        Code for reproducing experiments in "Improved Training of Wasserstein GANs".
        https://github.com/igul222/improved_wgan_training
    """
    def __init__(self, gamma=10., eps=1e-12, num_iter=1, use_amp=False):

        super(WGANGradientPenalty, self).__init__()

        self.gamma = gamma
        self.eps = eps
        self.num_iter = num_iter
        self.use_amp = use_amp
        self.to_backprop = True
        
    def forward(self, model, device, real_sample, fake_sample, scaler=None):

        batch_size = real_sample['data'].size(0)
        latent_shape = (1,)*(real_sample['data'].dim() - 1)
        # Calculate interpolation
        alpha = torch.rand(batch_size, *latent_shape, device=device)
        alpha = alpha.expand_as(real_sample['data'])
        # difference = fake_sample - real_sample
        # interpolation = real_sample + alpha*difference
        interpolation = {'data': alpha*real_sample['data'] + (1 - alpha)*fake_sample['data']}
        interpolation['data'].requires_grad_(True)
        # Calculate probability of interpolated examples
        with autocast() if self.use_amp else nullcontext():
            err_interpolation = model(interpolation)['data']
        if self.use_amp and scaler is not None:
            err_interpolation = scaler.scale(err_interpolation)
        grad_outputs = torch.ones(err_interpolation.size(), device=device)
        # Calculate gradients of probabilities with respect to examples
        gradients = autograd.grad(outputs=err_interpolation,
                                  inputs=interpolation['data'],
                                  grad_outputs=grad_outputs,
                                  create_graph=True,
                                  retain_graph=True,
                                  only_inputs=True)[0]
        if self.use_amp and scaler is not None:
            gradients = gradients/scaler.get_scale()

        with autocast() if self.use_amp else nullcontext():
            # Gradients have shape (batch_size, num_channels, img_width, img_height),
            # so flatten to easily take norm per example in batch
            gradients = gradients.view(batch_size, -1)
            # Derivatives of the gradient close to 0 can cause problems because of
            # the square root, so manually calculate norm and add epsilon
            slopes = torch.sqrt(torch.sum(gradients**2, dim=1) + self.eps)

            return self.gamma*((slopes - 1)**2).mean()


class WGANLipschitzPenalty(nn.Module):
    """
    Calculates the Lipschitz penalty of Wasserstein GAN.
    
    Parameters
    ----------
    gamma : float, optional (default 10.)
        Weight of the Lipschitz penalty.
    eps : float, optional (default 1e-12)
        Epsilon to add to the norm to avoid null gradient.
    num_iter : int, optional (default 1)
        Number of iterations before applying regularization to the loss function,
        aka lazy regularization.
    use_amp : bool, optional (default False)
        If True, uses automatic mixed precision.

    References
    ----------
    Petzka, H., Fischer, A., Lukovnikov, D. (2018).
        On the regularization of Wasserstein GANs.
        arXiv preprint arXiv:1709.08894, https://arxiv.org/abs/1709.08894
    """
    def __init__(self, gamma=10., eps=1e-12, num_iter=1, use_amp=False):

        super(WGANLipschitzPenalty, self).__init__()

        self.gamma = gamma
        self.eps = eps
        self.num_iter = num_iter
        self.use_amp = use_amp
        self.to_backprop = True
        
    def forward(self, model, device, real_sample, fake_sample, scaler=None):

        batch_size = real_sample['data'].size(0)
        latent_shape = (1,)*(real_sample['data'].dim() - 1)
        # Calculate interpolation
        alpha = torch.rand(batch_size, *latent_shape, device=device)
        alpha = alpha.expand_as(real_sample['data'])
        # difference = fake_sample - real_sample
        # interpolation = real_sample + alpha*difference
        interpolation = {'data': alpha*real_sample['data'] + (1 - alpha)*fake_sample['data']}
        interpolation['data'].requires_grad_(True)
        # Calculate probability of interpolated examples
        with autocast() if self.use_amp else nullcontext():
            err_interpolation = model(interpolation)['data']
        if self.use_amp and scaler is not None:
            err_interpolation = scaler.scale(err_interpolation)
        grad_outputs = torch.ones(err_interpolation.size(), device=device)
        # Calculate gradients of probabilities with respect to examples
        gradients = autograd.grad(outputs=err_interpolation,
                                  inputs=interpolation['data'],
                                  grad_outputs=grad_outputs,
                                  create_graph=True,
                                  retain_graph=True,
                                  only_inputs=True)[0]
        if self.use_amp and scaler is not None:
            gradients = gradients/scaler.get_scale()

        with autocast() if self.use_amp else nullcontext():
            # Gradients have shape (batch_size, num_channels, img_width, img_height),
            # so flatten to easily take norm per example in batch
            gradients = gradients.view(batch_size, -1)
            # Derivatives of the gradient close to 0 can cause problems because of
            # the square root, so manually calculate norm and add epsilon
            slopes = torch.sqrt(torch.sum(gradients**2, dim=1) + self.eps)
            
            regularization = torch.max(torch.zeros_like(slopes, device=device), slopes - 1)**2

            return self.gamma*regularization.mean()


################################################################################
# CT-GAN consistency term

class CTGANConsistencyTerm(nn.Module):
    """
    Calculates the consistency term of CTGAN.
    
    Parameters
    ----------
    gamma : float, optional (default 2.)
        Weight of the consistency term.
    M : float, optional (default 0.1)
        Constant to ensure the Lipschitz continuity.
    num_iter : int, optional (default 1)
        Number of iterations before applying regularization to the loss function,
        aka lazy regularization.
    use_amp : bool, optional (default False)
        If True, uses automatic mixed precision.

    References
    ----------
    Wei, X., Gong, B., Liu, Z., Lu, W., Wang, L. (2018).
        Improving the Improved Training of Wasserstein GANs: A Consistency Term and Its Dual Effect.
        arXiv preprint arXiv:1803.01541, https://arxiv.org/abs/1803.01541
    """
    def __init__(self, gamma=2., M=0.1, num_iter=1, use_amp=False):

        super(CTGANConsistencyTerm, self).__init__()

        self.gamma = gamma
        self.M = M
        self.num_iter = num_iter
        self.use_amp = use_amp
        self.to_backprop = True
        
    def forward(self, model, device, real_sample, fake_sample=None, scaler=None):

        batch_size = real_sample['data'].size(0)
        latent_shape = (1,)*(real_sample['data'].dim() - 1)

        with autocast() if self.use_amp else nullcontext():
            err_real_1 = model(real_sample, return_second_to_last=True)
            err_real_1['data'] = torch.reshape(err_real_1['data'], (batch_size,) + latent_shape)
            err_real_2 = model(real_sample, return_second_to_last=True)
            err_real_2['data'] = torch.reshape(err_real_2['data'], (batch_size,) + latent_shape)

            consistency_term = (err_real_1['data'] - err_real_2['data']).norm(2, dim=1) \
                            + 0.1*(err_real_1['second_to_last'] - err_real_2['second_to_last']).norm(2, dim=1) - self.M
            consistency_term = torch.max(consistency_term,
                                        torch.zeros_like(consistency_term, device=device))

            return self.gamma*consistency_term.mean()


################################################################################
# DRAGAN gradient penalty

class DRAGANGradientPenalty(nn.Module):
    """
    Calculates the gradient penalty of DRAGAN.
    
    Parameters
    ----------
    gamma : float, optional (default 10)
        Weight of the gradient penalty.
    c : float, optional (default 10)
        Weight of the perturbation of the real sample in the penalty.
    k : float, optional (default 1)
        Center of the gradient.
    eps : float, optional (default 1e-12)
        Epsilon to add to the norm to avoid null gradient.
    num_iter : int, optional (default 1)
        Number of iterations before applying regularization to the loss function,
        aka lazy regularization.
    use_amp : bool, optional (default False)
        If True, uses automatic mixed precision.

    References
    ----------
    Kodali, N., Abernethy, J., Hays, J., & Kira, Z. (2017).
        On convergence and stability of GANs.
        arXiv preprint arXiv:1705.07215, https://arxiv.org/abs/1705.07215
    Kodali, N. (2017).
        DRAGAN (Deep Regret Analytic Generative Adversarial Networks).
        https://github.com/kodalinaveen3/DRAGAN
    """
    def __init__(self, gamma=10., c=10., k=1., eps=1e-12, num_iter=1, use_amp=False):

        super(DRAGANGradientPenalty, self).__init__()

        self.gamma = gamma
        self.c = c
        self.k = k
        self.eps = eps
        self.num_iter = num_iter
        self.use_amp = use_amp
        self.to_backprop = True
        
    def forward(self, model, device, real_sample, fake_sample=None, scaler=None):

        batch_size = real_sample['data'].size(0)
        latent_shape = (1,)*(real_sample['data'].dim() - 1)
        # Calculate interpolation
        alpha = torch.rand(batch_size, *latent_shape, device=device)
        alpha = alpha.expand_as(real_sample['data'])
        # difference = real_sample + 0.5*real_sample.std()*torch.rand(real_sample.size(), device=device) - real_sample
        # interpolation = real_sample + alpha*difference
        # perturbed_sample = real_sample + 0.5*real_sample.std()*torch.rand(real_sample.size(), device=device)
        # perturbed_sample = real_sample + self.c*torch.normal(torch.zeros(real_sample.size(), device=device), real_sample.std().item())
        perturbed_sample = real_sample['data'] + self.c*real_sample['data'].std()*torch.randn(real_sample['data'].size(), device=device)
        interpolation = {'data': alpha*real_sample['data'] + (1 - alpha)*perturbed_sample}
        interpolation['data'].requires_grad_(True)
        # Calculate probability of interpolated examples
        with autocast() if self.use_amp else nullcontext():
            err_interpolations = model(interpolation)['data']
        if self.use_amp and scaler is not None:
            err_interpolations = scaler.scale(err_interpolations)
        grad_outputs = torch.ones(err_interpolations.size(), device=device)
        # Calculate gradients of probabilities with respect to examples
        gradients = autograd.grad(outputs=err_interpolations,
                                  inputs=interpolation['data'],
                                  grad_outputs=grad_outputs,
                                  create_graph=True,
                                  retain_graph=True,
                                  only_inputs=True)[0]
        if self.use_amp and scaler is not None:
            gradients = gradients/scaler.get_scale()

        with autocast() if self.use_amp else nullcontext():
            # Gradients have shape (batch_size, num_channels, img_width, img_height),
            # so flatten to easily take norm per example in batch
            gradients = gradients.view(batch_size, -1)
            # Derivatives of the gradient close to 0 can cause problems because of
            # the square root, so manually calculate norm and add epsilon
            slopes = torch.sqrt(torch.sum(gradients**2, dim=1) + self.eps)

            return self.gamma*((slopes - self.k)**2).mean()


################################################################################
# R1- and R2-regularization

class R1Regularization(nn.Module):
    """
    Calculates the R1 gradient penalty.
    
    Parameters
    ----------
    gamma : float, optional (default 10.)
        Weight of the gradient penalty.
    num_iter : int, optional (default 1)
        Number of iterations before applying regularization to the loss function,
        aka lazy regularization.
    use_amp : bool, optional (default False)
        If True, uses automatic mixed precision.

    References
    ----------
    Mescheder, L. (2020).
        Stability and Expressiveness of Deep Generative Models.
        PhD Thesis, Universitat Tubingen, https://hdl.handle.net/10900/106074
    """
    def __init__(self, gamma=10., num_iter=1, use_amp=False):

        super(R1Regularization, self).__init__()

        self.gamma = gamma
        self.num_iter = num_iter
        self.use_amp = use_amp
        self.to_backprop = True
        
    def forward(self, model, device, real_sample, fake_sample=None, scaler=None):

        batch_size = real_sample['data'].size(0)
        real_sample['data'].requires_grad_(True)
        # Calculate probability of the real sample
        with autocast() if self.use_amp else nullcontext():
            err_real = model(real_sample)['data']
        if self.use_amp and scaler is not None:
            err_real = scaler.scale(err_real)
        grad_outputs = torch.ones(err_real.size(), device=device)
        # Calculate gradients of probabilities with respect to the example
        gradients = autograd.grad(outputs=err_real,
                                  inputs=real_sample['data'],
                                  grad_outputs=grad_outputs,
                                  create_graph=True,
                                  retain_graph=True,
                                  only_inputs=True)[0]
        if self.use_amp and scaler is not None:
            gradients = gradients/scaler.get_scale()

        with autocast() if self.use_amp else nullcontext():
            # Gradients have shape (batch_size, num_channels, img_width, img_height),
            # so flatten to easily take norm per example in batch
            gradients = gradients.view(batch_size, -1)

            return self.gamma*torch.sum(gradients**2, dim=1).mean()


class R2Regularization(nn.Module):
    """
    Calculates the R2 gradient penalty.
    
    Parameters
    ----------
    gamma : float, optional (default 10.)
        Weight of the gradient penalty.
    num_iter : int, optional (default 1)
        Number of iterations before applying regularization to the loss function,
        aka lazy regularization.
    use_amp : bool, optional (default False)
        If True, uses automatic mixed precision.

    References
    ----------
    Mescheder, L. (2020).
        Stability and Expressiveness of Deep Generative Models.
        PhD Thesis, Universitat Tubingen, https://hdl.handle.net/10900/106074
    """
    def __init__(self, gamma=10., num_iter=1, use_amp=False):

        super(R2Regularization, self).__init__()

        self.gamma = gamma
        self.num_iter = num_iter
        self.use_amp = use_amp
        self.to_backprop = True
        
    def forward(self, model, device, real_sample, fake_sample, scaler=None):

        batch_size = fake_sample['data'].size(0)
        fake_sample['data'].requires_grad_(True)
        # Calculate probability of the fake sample
        with autocast() if self.use_amp else nullcontext():
            err_fake = model(fake_sample)['data']
        if self.use_amp and scaler is not None:
            err_fake = scaler.scale(err_fake)
        grad_outputs = torch.ones(err_fake.size(), device=device)
        # Calculate gradients of probabilities with respect to the example
        gradients = autograd.grad(outputs=err_fake,
                                  inputs=fake_sample['data'],
                                  grad_outputs=grad_outputs,
                                  create_graph=True,
                                  retain_graph=True,
                                  only_inputs=True)[0]
        if self.use_amp and scaler is not None:
            gradients = gradients/scaler.get_scale()

        with autocast() if self.use_amp else nullcontext():
            # Gradients have shape (batch_size, num_channels, img_width, img_height),
            # so flatten to easily take norm per example in batch
            gradients = gradients.view(batch_size, -1)

            return self.gamma*torch.sum(gradients**2, dim=1).mean()


################################################################################
# Orthogonal regularization

class OrthoRegularization(nn.Module):
    """
    Calculates the orthogonal regularization.
    
    Parameters
    ----------
    gamma : float, optional (default 10.)
        Weight of the gradient penalty.
    blacklist : list, optional (default None)
        List of parameters to ignore.
    num_iter : int, optional (default 1)
        Number of iterations before applying regularization to the loss function,
        aka lazy regularization.
    use_amp : bool, optional (default False)
        If True, uses automatic mixed precision.

    References
    ----------
    Brock, A., Lim, T., Ritchie, J.M., Weston, N. (2016).
        Neural photo editing with introspective adversarial networks
        arXiv preprint arXiv:1609.07093, https://arxiv.org/abs/1609.07093
    Brock, A., Donahue, J., Simonyan, K. (2018).
        Large Scale GAN Training for High Fidelity Natural Image Synthesis
        arXiv preprint arXiv:1809.11096v1, https://arxiv.org/abs/1809.11096v1
    Brock, A. (2019).
        BigGAN-PyTorch
        https://github.com/ajbrock/BigGAN-PyTorch
    """
    def __init__(self, gamma=1e-4, blacklist=None, num_iter=1, use_amp=False):

        super(OrthoRegularization, self).__init__()

        self.gamma = gamma
        self.use_amp = use_amp
        self.blacklist = blacklist if blacklist is not None else []
        self.num_iter = num_iter
        self.to_backprop = False
        
    def forward(self, model, device, real_sample, fake_sample=None, scaler=None):

        with torch.no_grad():
            for param in model.parameters():
                # Only apply this to parameters with at least 2 axes, and not in the blacklist
                if len(param.shape) < 2 or any([param is item for item in self.blacklist]):
                    continue
                with autocast() if self.use_amp else nullcontext():
                    w = param.view(param.shape[0], -1)
                    gradients = 2.*torch.mm(torch.mm(w, w.t())*(1. - torch.eye(w.shape[0], device=w.device)), w)
                    param.grad.data += self.gamma*gradients.view(param.shape)


################################################################################
# Law of superposition

class LoSRegularization(nn.Module):
    """
    Calculates a regularization using the law of superposition.
    
    Parameters
    ----------
    channel : int, optional (default 1)
        Channel containing the geological time property.
    gamma : float, optional (default 10.)
        Weight of the gradient penalty.
    num_iter : int, optional (default 1)
        Number of iterations before applying regularization to the loss function,
        aka lazy regularization.
    """
    def __init__(self, channel=1, gamma=10., num_iter=1):

        super(LoSRegularization, self).__init__()

        self.channel = channel
        self.gamma = gamma
        self.num_iter = num_iter
        self.to_backprop = True

    def forward(self, model, device, real_sample, fake_sample, scaler=None):

        axes = tuple(range(fake_sample['data'][:, self.channel].ndim))[1:]
        distances = 1. - torch.sum(fake_sample['data'][:, self.channel, ..., 1:] >= fake_sample['data'][:, self.channel, ..., :-1], axis=axes)/fake_sample['data'][0, self.channel, ..., 1:].nelement()

        return torch.mean(distances)


################################################################################
# Hinge loss

class GANHingeLoss(nn.Module):
    """
    Creates a criterion that measures the GAN hinge loss between each element in
    the input and target.

    Parameters
    ----------
    for_discriminator : bool, optional (default True)
        If true, computes the hinge loss for the discriminator, otherwise computes
        it for the generator.
    """
    def __init__(self, for_discriminator=True):

        super(GANHingeLoss, self).__init__()

        self.for_discriminator = for_discriminator
        
    def forward(self, input, target=None):

        if self.for_discriminator == True:
            return torch.mean(torch.relu(1. - target*input))
        else:
            return -torch.mean(input)

################################################################################
# Continuous latent code loss

class ContinuousLatentLoss(nn.GaussianNLLLoss):
    """
    Loss for a continuous latent code using a Gaussian negative log-likelihood.

    Parameters
    ----------
    gamma : float, optional (default 0.1)
        Weight of the loss.
    full : bool, optional (default False)
        Includes the constant term in the loss calculation.
    eps : float, optional (default 1e-6)
        Value used to clamp `var`, for stability.
    reduction : str, optional (default 'mean')
        Specifies the reduction to apply to the output: `'none'` | `'mean'` | `'sum'`:
            `'none'`: no reduction will be applied.
            `'mean'`: the output is the average of all batch member losses.
            `'sum'`: the output is the sum of all batch member losses.
    """
    def __init__(self, gamma=0.1, full=False, eps=1e-6, reduction='mean'):

        super(ContinuousLatentLoss, self).__init__(full=full,
                                                   eps=eps,
                                                   reduction=reduction)

        self.gamma = gamma

    def forward(self, input, target):

        return self.gamma*super(ContinuousLatentLoss, self).forward(input[:, ::2],
                                                                    target,
                                                                    torch.sqrt(torch.exp(input[:, 1::2])))
