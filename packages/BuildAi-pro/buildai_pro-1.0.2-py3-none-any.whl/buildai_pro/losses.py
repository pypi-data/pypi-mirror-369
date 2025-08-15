import numpy as np
from .tensor import Tensor
def mse(pred: Tensor, target: Tensor):
    return float(((pred.data - target.data)**2).mean())
def mse_grad(pred: Tensor, target: Tensor):
    n = pred.data.size
    return Tensor(2*(pred.data - target.data)/n)
def cross_entropy(pred_probs: Tensor, target_onehot: Tensor):
    p = pred_probs.data
    eps = 1e-12
    return float(- (target_onehot.data * np.log(p + eps)).sum() / p.shape[0])
def cross_entropy_grad(pred_probs: Tensor, target_onehot: Tensor):
    probs = pred_probs.data
    target = target_onehot.data
    return Tensor((probs - target)/ (probs.shape[0] if probs.ndim>1 else 1))
