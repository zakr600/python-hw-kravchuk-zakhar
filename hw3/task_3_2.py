import numpy as np
from matrix_lib import MatrixND

np.random.seed(0)

A = MatrixND(np.random.randint(0, 10, (10, 10)))
B = MatrixND(np.random.randint(0, 10, (10, 10)))

(A + B).to_file("artifacts/3_2/matrix+.txt")
(A * B).to_file("artifacts/3_2/matrix*.txt")
(A @ B).to_file("artifacts/3_2/matrix@.txt")
