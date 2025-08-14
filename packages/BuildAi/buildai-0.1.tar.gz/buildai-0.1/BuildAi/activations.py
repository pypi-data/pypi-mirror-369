import numpy as np
from .tensor import Tensor

def relu(t: Tensor):
    return Tensor(np.maximum(0, t.data))

def sigmoid(t: Tensor):
    return Tensor(1 / (1 + np.exp(-t.data)))
