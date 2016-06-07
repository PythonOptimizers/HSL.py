"""Illustrates usage of PyMa27 or PyMa57 for factorization of SQP matrices.


For a description and properties of Symmetric Quasi-Definite (sqd) matrices,
see

 R. J. Vanderbei, Symmetric Quasi-Definite Matrices,
 SIAM Journal on Optimization, 5(1), 100-113, 1995.

Example usage: python demo_sqd.py bcsstk18.mtx bcsstk11.mtx

D. Orban, Montreal, December 2007.
"""

try:
    from hsl.solvers.pyma57 import PyMa57Solver as LBLContext
except ImportError:
    from hsl.solvers.pyma27 import PyMa27Solver as LBLContext

from pysparse.sparse import spmatrix
from pysparse.sparse.pysparseMatrix import PysparseMatrix as sp
import numpy as np
import timeit
import sys

if len(sys.argv) < 3:
    sys.stderr.write('Please supply two positive definite matrices as input')
    sys.stderr.write(' in MatrixMarket format.\n')
    sys.exit(1)

# Create symmetric quasi-definite matrix K
A = sp(matrix=spmatrix.ll_mat_from_mtx(sys.argv[1]))
C = sp(matrix=spmatrix.ll_mat_from_mtx(sys.argv[2]))

nA = A.shape[0]
nC = C.shape[0]
# K = spmatrix.ll_mat_sym(nA + nC, A.nnz + C.nnz + min(nA,nC))
K = sp(size=nA + nC, sizeHint=A.nnz + C.nnz + min(nA, nC), symmetric=True)
K[:nA, :nA] = A
K[nA:, nA:] = -C
# K[nA:,nA:].scale(-1.0)
idx = np.arange(min(nA, nC), dtype=np.int)
K.put(1, nA + idx, idx)

# Create right-hand side rhs=K*e
e = np.ones(nA + nC)
# rhs = np.empty(nA+nC)
# K.matvec(e,rhs)
rhs = K * e

# Factorize and solve Kx = rhs, knowing K is sqd
t = timeit.default_timer()
LDL = LBLContext(K, sqd=True)
t = timeit.default_timer() - t
sys.stderr.write('Factorization time with sqd=True : %5.2fs   ' % t)
LDL.solve(rhs, get_resid=False)
sys.stderr.write('Error: %7.1e\n' % np.linalg.norm(LDL.x - e, ord=np.Inf))

# Do it all over again, pretending we don't know K is sqd
t = timeit.default_timer()
LBL = LBLContext(K)
t = timeit.default_timer() - t
sys.stderr.write('Factorization time with sqd=False: %5.2fs   ' % t)
LBL.solve(rhs, get_resid=False)
sys.stderr.write('Error: %7.1e\n' % np.linalg.norm(LBL.x - e, ord=np.Inf))
