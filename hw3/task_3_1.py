import numpy as np
from matrix_lib import Matrix

np.random.seed(0)

A = Matrix(np.random.randint(0, 10, (10, 10)))
B = Matrix(np.random.randint(0, 10, (10, 10)))

A_plus_B = A + B
A_mul_B = A * B
A_matmul_B = A @ B

A_plus_B.to_file("artifacts/3_1/matrix+.txt")
A_mul_B.to_file("artifacts/3_1/matrix*.txt")
A_matmul_B.to_file("artifacts/3_1/matrix@.txt")
