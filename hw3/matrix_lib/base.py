import numpy as np


class Matrix:
    def __init__(self, data):
        self.data = np.asarray(data)

    def _check_same_shape(self, other):
        if self.data.shape != other.data.shape:
            raise ValueError("Matrices must have the same shape")

    def __add__(self, other):
        self._check_same_shape(other)
        return Matrix(self.data + other.data)

    def __mul__(self, other):
        self._check_same_shape(other)
        return Matrix(self.data * other.data)

    def __matmul__(self, other):
        if self.data.shape[1] != other.data.shape[0]:
            raise ValueError("Invalid shapes for matrix multiplication")
        return Matrix(self.data @ other.data)

    def to_file(self, path):
        np.savetxt(path, self.data, fmt="%d")
