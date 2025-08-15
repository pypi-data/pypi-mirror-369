import numpy as np
class Tensor:
    def __init__(self, data):
        if isinstance(data, np.ndarray):
            self.data = data.astype(float)
        else:
            self.data = np.array(data, dtype=float)
    def copy(self):
        return Tensor(self.data.copy())
    def tolist(self):
        return self.data.tolist()
    def shape(self):
        return self.data.shape
    def __repr__(self):
        return f"Tensor(shape={self.data.shape})"
