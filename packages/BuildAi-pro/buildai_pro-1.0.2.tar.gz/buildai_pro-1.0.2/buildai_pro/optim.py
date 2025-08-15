import numpy as np
class SGD:
    def __init__(self, params, lr=0.01):
        self.params = params
        self.lr = lr
    def step(self):
        for p in self.params:
            if hasattr(p, 'step'):
                p.step(self.lr)
class Adam:
    def __init__(self, params, lr=0.001, beta1=0.9, beta2=0.999, eps=1e-8):
        self.params = params
        self.lr = lr
        self.beta1 = beta1; self.beta2 = beta2; self.eps = eps
        self.m = {}
        self.v = {}
        self.t = 0
    def step(self):
        import numpy as np
        self.t += 1
        for p in self.params:
            if not hasattr(p, 'W'):
                continue
            pid = id(p)
            if pid not in self.m:
                self.m[pid] = [np.zeros_like(p.W), np.zeros_like(p.b) if p.b is not None else None]
                self.v[pid] = [np.zeros_like(p.W), np.zeros_like(p.b) if p.b is not None else None]
            mW, mb = self.m[pid]
            vW, vb = self.v[pid]
            gW = p.dW
            gb = p.db if p.db is not None else None
            mW[:] = self.beta1 * mW + (1 - self.beta1) * gW
            vW[:] = self.beta2 * vW + (1 - self.beta2) * (gW * gW)
            mW_hat = mW / (1 - self.beta1 ** self.t)
            vW_hat = vW / (1 - self.beta2 ** self.t)
            p.W -= self.lr * mW_hat / (np.sqrt(vW_hat) + self.eps)
            if p.b is not None and gb is not None:
                mb[:] = self.beta1 * mb + (1 - self.beta1) * gb
                vb[:] = self.beta2 * vb + (1 - self.beta2) * (gb * gb)
                mb_hat = mb / (1 - self.beta1 ** self.t)
                vb_hat = vb / (1 - self.beta2 ** self.t)
                p.b -= self.lr * mb_hat / (np.sqrt(vb_hat) + self.eps)
