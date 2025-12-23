import numpy as np
from matrix_lib import Matrix, CachedMatrix

A = Matrix([[1, 2], [3, 4]])
C = Matrix([[3, 4], [5, -2]])

cachedA = CachedMatrix(A.data)
cachedC = CachedMatrix(C.data) 



B = CachedMatrix([[1, 0], [1, 1]])
D = B

AB = CachedMatrix((A @ B).data)
CD = CachedMatrix((C @ D).data)

assert hash(cachedA) == hash(cachedC), f"Hashes should be equal for A ({hash(A)}) and C ({hash(C)})"
assert not ((AB.data == CD.data).all()), "AB should not be equals CD"
assert A != C, "A should not be equal C"
assert B == D, "B should be equal D"

np.savetxt("artifacts/3_3/A.txt", A.data, fmt="%d")
np.savetxt("artifacts/3_3/B.txt", B.data, fmt="%d")
np.savetxt("artifacts/3_3/C.txt", C.data, fmt="%d")
np.savetxt("artifacts/3_3/D.txt", D.data, fmt="%d")

np.savetxt("artifacts/3_3/AB.txt", AB.data, fmt="%d")
np.savetxt("artifacts/3_3/CD.txt", CD.data, fmt="%d")

with open("artifacts/3_3/hash.txt", "w") as f:
    f.write(f"hash(AB) = {hash(AB)}\n")
    f.write(f"hash(CD) = {hash(CD)}\n")
