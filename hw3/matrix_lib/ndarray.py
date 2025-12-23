import numpy as np
from numpy.lib.mixins import NDArrayOperatorsMixin

from .mixins import FileMixin, PrettyPrintMixin, AccessorMixin


class MatrixND(
    NDArrayOperatorsMixin,
    FileMixin,
    PrettyPrintMixin,
    AccessorMixin,
):
    __array_priority__ = 1000

    def __init__(self, data):
        self._data = np.asarray(data)

    def __array__(self, dtype=None):
        return np.asarray(self._data, dtype=dtype)

    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        arrays = [
            x._data if isinstance(x, MatrixND) else x
            for x in inputs
        ]

        result = getattr(ufunc, method)(*arrays, **kwargs)

        if isinstance(result, tuple):
            return tuple(MatrixND(x) for x in result)

        return MatrixND(result)
