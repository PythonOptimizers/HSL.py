import numpy as np

from hsl.solvers.src._cyma57_numpy_INT32_FLOAT64 import NumpyMA57Solver_INT32_FLOAT64
import sys

n = 5
nnz = 7
A = np.array([[2.0,3.0,0,0,0], [0,0,4.0,0,6.0], [0,0,1,5,0], [0,0,0,0,0], [0,0,0,0,1]], dtype=np.float32)
arow = np.array([0,0,1,1,2,2,4], dtype=np.int32)
acol = np.array([0,1,2,4,2,3,4], dtype=np.int32)
aval = np.array([2.0,3.0,4.0,6.0,1.0,5.0,1.0], dtype=np.float64)

rhs = np.array([8,45,31,15,17], dtype=np.float64)


context = NumpyMA57Solver_INT32_FLOAT64(n, n, nnz)
context.get_matrix_data(arow, acol, aval)

context.analyze()

context.factorize()

print 'Solve:'
residual = np.zeros(n, 'd')
x  = context.solve(rhs, residual, False)
print '  x:'
print x

print 'Fetch_perm:'
perm = context.fetch_perm()
print '  perm:'
print perm

print 'Refine:'
(new_x, new_rhs) = context.refine(x, rhs, 5)
print '  cond: ', context.cond
print '  new_x: '
print new_x
print x
print '  new_rhs: '
print new_rhs
print rhs

