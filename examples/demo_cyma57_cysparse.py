from cysparse.sparse.ll_mat import *
import cysparse.types.cysparse_types as types
import numpy as np

from hsl.solvers.src._cyma57_cysparse_INT32_FLOAT64 import CySparseMA57Solver_INT32_FLOAT64
import sys


A = LLSparseMatrix(mm_filename=sys.argv[1], itype=types.INT32_T, dtype=types.FLOAT64_T)

print A


(n, m) = A.shape
e = np.ones(n, 'd')
#rhs = np.zeros(n, 'd')
rhs = A*e


context = CySparseMA57Solver_INT32_FLOAT64(A.nrow, A.ncol, A.nnz)
context.get_matrix_data(A)

context.analyze()

context.factorize()

print 'Fetch_perm:'
perm = context.fetch_perm()
print '  perm:'
print perm


print 'Solve:'
x, residual  = context.solve(rhs, True)
print '  x:'
print x
print '  residual:'
print residual

print 'Refine:'
(new_x, new_res) = context.refine(x, rhs, residual, 5)
print '  cond: ', context.cond
print '  new_x: '
print new_x
print '  new_res: '
print new_res

