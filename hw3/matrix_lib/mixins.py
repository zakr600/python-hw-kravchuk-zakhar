import numpy as np


class FileMixin:
    def to_file(self, path):
        np.savetxt(path, self.data, fmt="%d")


class PrettyPrintMixin:
    def __str__(self):
        return str(self.data)


class AccessorMixin:
    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = np.asarray(value)


# Хеш-функция, возвращающая сумму всех элементов матрицы
class HashMixin:
    def __hash__(self):
        return int(self.data.sum())
