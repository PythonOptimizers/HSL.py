"""Exemple from MA27 spec sheet: http://www.hsl.rl.ac.uk/specs/ma57.pdf."""

import sys
import numpy as np
from hsl.solvers.src._cyma27_numpy_INT32_FLOAT64 import NumpyMA27Solver_INT32_FLOAT64

n = 5
nnz = 7
A = np.array([[2.0, 3.0, 0, 0, 0], [0, 0, 4.0, 0, 6.0], [0, 0, 1, 5, 0], [
             0, 0, 0, 0, 0], [0, 0, 0, 0, 1]], dtype=np.float32)
arow = np.array([0, 0, 1, 1, 2, 2, 4], dtype=np.int32)
acol = np.array([0, 1, 2, 4, 2, 3, 4], dtype=np.int32)
aval = np.array([2.0, 3.0, 4.0, 6.0, 1.0, 5.0, 1.0], dtype=np.float64)

rhs = np.array([8, 45, 31, 15, 17], dtype=np.float64)


context = NumpyMA27Solver_INT32_FLOAT64(n, n, nnz)
context.get_matrix_data(arow, acol, aval)

context.analyze()

context.factorize()

print 'Fetch_perm:'
perm = context.fetch_perm()
print '  perm:'
print perm


print 'Solve:'
x, residual = context.solve(rhs, True)
# x = context.solve(rhs, False)
print '  x:'
print x
print '  residual:'
print residual

print 'Refine:'
(new_x, new_res) = context.refine(x, rhs, residual, 1e-8, 5)
print '  new_x: '
print new_x
print '  new_res: '
print new_res
