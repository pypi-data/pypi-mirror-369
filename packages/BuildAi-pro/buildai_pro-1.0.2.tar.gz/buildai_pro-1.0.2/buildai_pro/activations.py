import numpy as np
from .tensor import Tensor
def relu(x: Tensor) -> Tensor:
    return Tensor(np.maximum(0, x.data))
def relu_grad(x: Tensor) -> Tensor:
    return Tensor((x.data > 0).astype(float))
def sigmoid(x: Tensor) -> Tensor:
    s = 1.0 / (1.0 + np.exp(-x.data))
    return Tensor(s)
def sigmoid_grad(x: Tensor) -> Tensor:
    s = 1.0 / (1.0 + np.exp(-x.data))
    return Tensor(s * (1 - s))
def softmax(x: Tensor) -> Tensor:
    z = x.data - np.max(x.data, axis=-1, keepdims=True)
    exps = np.exp(z)
    return Tensor(exps / np.sum(exps, axis=-1, keepdims=True))
