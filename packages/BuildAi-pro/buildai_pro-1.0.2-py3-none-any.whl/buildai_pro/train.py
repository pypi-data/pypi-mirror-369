import numpy as np
from .tensor import Tensor
from .losses import mse, mse_grad, cross_entropy, cross_entropy_grad
def train(model, X, y, epochs=10, batch_size=32, optimizer=None, loss='mse', verbose=1, checkpoint=None):
    n = X.shape[0]
    for epoch in range(1, epochs+1):
        perm = np.random.permutation(n)
        total_loss = 0.0
        for i in range(0, n, batch_size):
            idx = perm[i:i+batch_size]
            xb = X[idx]
            yb = y[idx]
            out = model.forward(Tensor(xb))
            if loss == 'mse':
                loss_val = mse(out, Tensor(yb))
                grad = mse_grad(out, Tensor(yb))
            else:
                probs = out
                loss_val = cross_entropy(probs, Tensor(yb))
                grad = cross_entropy_grad(probs, Tensor(yb))
            total_loss += loss_val * len(idx)
            model.backward(grad)
            if optimizer:
                optimizer.step()
        if verbose:
            print(f"Epoch {epoch}/{epochs} - loss: {total_loss / n:.6f}")
        if checkpoint:
            from .io import save_model
            save_model(model, checkpoint.format(epoch=epoch))
