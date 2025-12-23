from .base import Matrix
from .mixins import HashMixin

_matmul_cache = {}


class CachedMatrix(Matrix, HashMixin):
    def __matmul__(self, other):
        key = (hash(self), hash(other))
        if key not in _matmul_cache:
            _matmul_cache[key] = super().__matmul__(other)
        return _matmul_cache[key]
