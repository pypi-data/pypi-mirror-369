import numpy as np

class Tensor:
    def __init__(self, data):
        self.data = np.array(data, dtype=np.float32)
        self.grad = np.zeros_like(self.data)

    def __add__(self, other):
        if isinstance(other, Tensor):
            return Tensor(self.data + other.data)
        return Tensor(self.data + other)

    def __mul__(self, other):
        if isinstance(other, Tensor):
            return Tensor(self.data * other.data)
        return Tensor(self.data * other)

    def __repr__(self):
        return f"Tensor({self.data})"
