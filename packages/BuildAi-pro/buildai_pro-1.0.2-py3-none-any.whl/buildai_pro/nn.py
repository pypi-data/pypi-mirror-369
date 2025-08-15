import numpy as np
from .tensor import Tensor
class Dense:
    def __init__(self, in_features, out_features, bias=True):
        self.in_features = int(in_features)
        self.out_features = int(out_features)
        limit = np.sqrt(6.0 / (self.in_features + self.out_features))
        self.W = np.random.uniform(-limit, limit, (self.in_features, self.out_features)).astype(float)
        self.b = np.zeros(self.out_features) if bias else None
        self.dW = np.zeros_like(self.W)
        self.db = np.zeros_like(self.b) if bias else None
        self._x = None
    def forward(self, x: Tensor) -> Tensor:
        self._x = x.data.copy()
        out = self._x.dot(self.W)
        if self.b is not None:
            out = out + self.b
        return Tensor(out)
    def backward(self, grad_out: Tensor) -> Tensor:
        x = self._x
        if x.ndim == 1:
            self.dW = np.outer(x, grad_out.data)
            if self.db is not None:
                self.db = grad_out.data.copy()
            grad_in = self.W.dot(grad_out.data)
        else:
            self.dW = x.T.dot(grad_out.data) / x.shape[0]
            if self.db is not None:
                self.db = grad_out.data.mean(axis=0)
            grad_in = grad_out.data.dot(self.W.T)
        return Tensor(grad_in)
    def step(self, lr):
        self.W -= lr * self.dW
        if self.b is not None:
            self.b -= lr * self.db
    def to_dict(self):
        return {'in': self.in_features, 'out': self.out_features, 'W': self.W.tolist(), 'b': None if self.b is None else self.b.tolist()}
    @classmethod
    def from_dict(cls, d):
        inst = cls(d['in'], d['out'], bias=(d.get('b') is not None))
        inst.W = np.array(d['W'], dtype=float)
        inst.b = None if d.get('b') is None else np.array(d['b'], dtype=float)
        return inst
class Sequential:
    def __init__(self, layers):
        self.layers = layers
    def forward(self, x: Tensor):
        out = x
        for l in self.layers:
            out = l.forward(out)
        return out
    def backward(self, grad: Tensor):
        g = grad
        for l in reversed(self.layers):
            g = l.backward(g)
        return g
    def step(self, lr):
        for l in self.layers:
            if hasattr(l, 'step'):
                l.step(lr)
class Model(Sequential):
    def predict(self, x): return self.forward(x)
