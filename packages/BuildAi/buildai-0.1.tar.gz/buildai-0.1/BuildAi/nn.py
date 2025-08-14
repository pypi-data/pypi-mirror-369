import numpy as np
from .tensor import Tensor

class Dense:
    def __init__(self, input_size, output_size):
        self.weights = Tensor(np.random.randn(input_size, output_size) * 0.01)
        self.bias = Tensor(np.zeros(output_size))

    def forward(self, x: Tensor):
        return Tensor(np.dot(x.data, self.weights.data) + self.bias.data)

def mse_loss(pred: Tensor, target: Tensor):
    return np.mean((pred.data - target.data) ** 2)
