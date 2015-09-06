from cysparse.sparse.ll_mat import *
import cysparse.types.cysparse_types as types
import numpy as np

from hsl.solvers._cyma57 import MA57Context
import sys


A = NewLLSparseMatrix(mm_filename=sys.argv[1], itype=types.INT64_T, dtype=types.FLOAT64_T)

print A


(n, m) = A.shape
e = np.ones(n, 'd')
#rhs = np.zeros(n, 'd')
rhs = A*e


context = MA57Context(A)

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



