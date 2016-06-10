# Demonstrate usage of PyMa27 abstract class for the solution of symmetric
# systems of linear equations.
# Example usage: python demo_ma27.py file1.mtx ... fileN.mtx
# where each fileK.mtx is in MatrixMarket format.

# from hsl.solvers.pyma27 import PyMa27Solver as LBLContext
from hsl.solvers.pyma57 import PyMa57Solver as LBLContext
from pysparse import spmatrix
from numpy.linalg import norm
import timeit
import numpy as np


def Hilbert(n):
    """The cream of ill conditioning: the Hilbert matrix.

    See Higham, "Accuracy and Stability of Numerical Algoriths", section 28.1.
    The matrix has elements H(i,j) = 1/(i+j-1) when indexed i,j=1..n.  However,
    here we index as i,j=0..n-1, so the elements are H(i,j) = 1/(i+j+1).
    """
    if n <= 0:
        return None
    if n == 1:
        return 1.0
    nnz = n * (n - 1) / 2
    H = spmatrix.ll_mat_sym(n, nnz)
    for i in range(n):
        for j in range(i + 1):
            H[i, j] = 1.0 / (i + j + 1)
    return H


def Ma27SpecSheet():
    """This is the example from the MA27 spec sheet.

    Solution should be [1,2,3,4,5]"""
    A = spmatrix.ll_mat_sym(5, 7)
    A[0, 0] = 2
    A[1, 0] = 3
    A[2, 1] = 4
    A[2, 2] = 1
    A[3, 2] = 5
    A[4, 1] = 6
    A[4, 4] = 1

    rhs = np.ones(5, 'd')
    rhs[0] = 8
    rhs[1] = 45
    rhs[2] = 31
    rhs[3] = 15
    rhs[4] = 17

    return (A, rhs)


def solve_system(A, rhs, itref_threshold=1.0e-6, nitrefmax=5, **kwargs):

    # Obtain Sils context object
    t = timeit.default_timer()
    LBL = LBLContext(A, **kwargs)
    t_analyze = timeit.default_timer() - t

    # Solve system and compute residual
    t = timeit.default_timer()
    LBL.solve(rhs)
    t_solve = timeit.default_timer() - t

    # Compute residual norm
    nrhsp1 = norm(rhs, ord=np.infty) + 1
    nr = norm(LBL.residual) / nrhsp1

    # If residual not small, perform iterative refinement
    LBL.refine(rhs, tol=itref_threshold, nitref=nitrefmax)
    nr1 = norm(LBL.residual, ord=np.infty) / nrhsp1

    return (LBL.x, LBL.residual, nr, nr1, t_analyze, t_solve, LBL.neig)

if __name__ == '__main__':
    import sys
    import os
    matrices = sys.argv[1:]

    hdr_fmt = '%-13s  %-11s  %-11s  %-11s  %-7s  %-7s  %-5s\n'
    res_fmt = '%-13s  %-11.5e  %-11.5e  %-11.5e  %-7.3f  %-7.3f  %-5d\n'
    hdrs = ('Name', 'Rel. resid.', 'Residual', 'Resid itref', 'Analyze',
            'Solve', 'neig')
    header = hdr_fmt % hdrs
    lhead = len(header)
    sys.stderr.write('-' * lhead + '\n')
    sys.stderr.write(header)
    sys.stderr.write('-' * lhead + '\n')

    # Solve example from the spec sheet
    (A, rhs) = Ma27SpecSheet()
    (x, r, nr, nr1, t_an, t_sl, neig) = solve_system(A, rhs)
    exact = np.arange(5, dtype='d') + 1
    relres = norm(x - exact) / norm(exact)
    sys.stdout.write(res_fmt %
                     ('Spec sheet', relres, nr, nr1, t_an, t_sl, neig))

    # Solve example with Hilbert matrix
    n = 10
    H = Hilbert(n)
    e = np.ones(n, 'd')
    rhs = np.empty(n, 'd')
    H.matvec(e, rhs)
    (x, r, nr, nr1, t_an, t_sl, neig) = solve_system(H, rhs)
    relres = norm(x - e) / norm(e)
    sys.stdout.write(res_fmt % ('Hilbert', relres, nr, nr1, t_an, t_sl, neig))

    # Process matrices given on the command line
    for matrix in matrices:
        M = spmatrix.ll_mat_from_mtx(matrix)
        (m, n) = M.shape
        if m != n:
            break
        e = np.ones(n, 'd')
        rhs = np.empty(n, 'd')
        M.matvec(e, rhs)
        (x, r, nr, nr1, t_an, t_sl, neig) = solve_system(M, rhs)
        relres = norm(x - e) / norm(e)
        probname = os.path.basename(matrix)
        if probname[-4:] == '.mtx':
            probname = probname[:-4]
        sys.stdout.write(res_fmt %
                         (probname, relres, nr, nr1, t_an, t_sl, neig))
    sys.stderr.write('-' * lhead + '\n')
