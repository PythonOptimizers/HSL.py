# -*- coding: utf-8 -*-
"""Ma57: Direct multifrontal solution of symmetric systems."""

from pysparse.sparse.pysparseMatrix import PysparseMatrix
from hsl.solvers import _pyma57
from sils import Sils


class PyMa57Solver(Sils):

    def __init__(self, A, factorize=True, **kwargs):
        u"""Instantiate a :class:`PyMa57Solver` object.

        Context to solve the square symmetric linear system of equations

            A x = b.

        A should be given in ll_mat format and should be symmetric.
        The system will first be analyzed and factorized, for later
        solution. Residuals will be computed dynamically if requested.

        The factorization is a multi-frontal variant of the Bunch-Parlett
        factorization, i.e.

            A = L B Lᵀ

        where L is unit lower triangular, and B is symmetric and block diagonal
        with either 1x1 or 2x2 blocks.

        A special option is available is the matrix A is known to be symmetric
        (positive or negative) definite, or symmetric quasi-definite (sqd).
        SQD matrices have the general form

            [ E   Gᵀ ]
            [ G  -F  ]

        where both E and F are positive definite. As a special case, positive
        definite matrices and negative definite matrices are sqd. SQD matrices
        can be factorized with potentially much sparser factors. Moreover, the
        matrix B reduces to a diagonal matrix.

        Currently accepted keyword arguments are:

        :keywords:
            :sqd:  Flag indicating symmetric quasi-definite matrix (default: False)

        Example:

        >>> import pyma57
        >>> import numpy
        >>> P = pyma57.PyMa57Solver(A)
        >>> P.solve(rhs, get_resid=True)
        >>> print numpy.linalg.norm(P.residual)

        PyMa57Solver relies on the sparse direct multifrontal code MA57
        from the Harwell Subroutine Library.

        From the MA57 spec sheet, 'In addition to being more efficient largely
        through its use of the Level 3 BLAS, it has many added features. Among
        these are: a fast mapping of data prior to a numerical factorization,
        the ability to modify pivots if the matrix is not definite, the
        efficient solution of several right-hand sides, a routine implementing
        iterative refinement, and the possibility of restarting the
        factorization should it run out of space.'


        References
        ----------

        1. I. S. Duff, "MA57 -- A New Code for the Solution of Sparse Symmetric
           Indefinite Systems", ACM Transactions on Mathematical Software (30),
           p. 118-144, 2004.
        2. I. S. Duff and J. K. Reid, "The Multifrontal Solution of Indefinite
           Sparse Symmetric Linear Systems", Transactions on Mathematical
           Software (9), p. 302--325, 1983.
        3. http://hsl.rl.ac.uk/hsl2007/hsl20074researchers.html
        """

        if isinstance(A, PysparseMatrix):
            thisA = A.matrix
        else:
            thisA = A

        super(PyMa57Solver, self).__init__(thisA, **kwargs)

        # Statistics on A
        self.nzFact = 0      # Number of nonzeros in factors
        self.nRealFact = 0   # Storage for real data of factors
        self.nIntFact = 0    # Storage for int  data of factors
        self.front = 0       # Largest front size
        self.n2x2pivots = 0  # Number of 2x2 pivots used
        self.neig = 0        # Number of negative eigenvalues detected
        self.rank = 0        # Matrix rank

        # Factors
        # self.L = spmatrix.ll_mat(self.n, self.n, 0)
        # self.B = spmatrix.ll_mat_sym(self.n, 0)

        # Analyze and factorize matrix
        self.context = _pyma57.analyze(thisA, self.sqd)
        self.factorized = False
        if factorize:
            self.factorize(thisA)
        return

    @property
    def inertia(self):
        u"""Return inertia of matrix A.

        Inertia of a matrix is given by (# of λ>0, # of λ<0, # λ=0).
        """
        if not self.factorized:
            raise TypeError("Factorization must be performed first.")
        return (self.rank - self.neig, self.neig, self.n - self.rank)

    def factorize(self, A):
        """Perform numerical factorization.

        Before this can be done, symbolic factorization (the `analyze` phase)
        must have been performed.

        The values of the elements of the matrix may have been altered since
        the analyze phase but the sparsity pattern must not have changed. Use
        the optional argument newA to specify the updated matrix if applicable.
        """

        if isinstance(A, PysparseMatrix):
            thisA = A.matrix
        else:
            thisA = A

        self.context.factorize(thisA)
        self.factorized = True

        (self.nzFact, self.nRealFact, self.nIntFact, self.front,
         self.n2x2pivots, self.neig, self.rank) = self.context.stats()

        self.isFullRank = (self.rank == self.n)
        return

    def solve(self, b, get_resid=True):
        """Solve the linear system of equations Ax = b.

        The solution will be found in self.x and residual in
        `self.residual`.
        """
        self.context.ma57(b, self.x, self.residual, get_resid)
        return None

    def refine(self, b, nitref=3, **kwargs):
        u"""Perform iterative refinement if necessary.

        Iterative refinement is performed until the scaled residual norm
        ‖b-Ax‖/(1+‖b‖) falls below the threshold 'tol' or until nitref steps
        are taken.
        Make sure you have called `solve()` with the same right-hand side b
        before calling `refine()`.
        The residual vector `self.residual` will be updated to reflect the
        updated approximate solution.

        By default, nitref = 3.
        """
        (self.cond, self.cond2, self.berr,
         self.berr2, self.dirError,
         self.matNorm, self.xNorm,
         self.relRes) = self.context.refine(self.x, self.residual, b, nitref)
        return None

    def fetch_perm(self):
        u"""Return the permutation vector p.

        Permutation vector is used
        to compute the factorization of A. Rows and columns
        were permuted so that

              Pᵀ A P = L B Lᵀ

        where i-th row of P is the p(i)-th row of the
        identity matrix, L is unit upper triangular and
        B is block diagonal with 1x1 and 2x2 blocks.
        """
        return self.context.fetchperm()

#     def fetch_lb(self):
#         """
#         fetch_lb() returns the factors L and B of A such that

#               P^T  A P = L  B  L^T

#         where P is as in fetch_perm(), L is unit upper
#         triangular and B is block diagonal with 1x1 and 2x2
#         blocks. Access to the factors is available as soon
#         as a PyMa27Solver has been instantiated.
#         """
#         self.context.fetchlb(self.L, self.B)
#         return None


if __name__ == '__main__':

    import sys
    import numpy as np

    from pysparse.sparse import spmatrix

    M = spmatrix.ll_mat_from_mtx(sys.argv[1])
    (m, n) = M.shape
    if m != n:
        sys.stderr('Matrix must be square')
        sys.exit(1)
    if not M.issym:
        sys.stderr('Matrix must be symmetric')
        sys.exit(2)
    e = np.ones(n, 'd')
    rhs = np.zeros(n, 'd')
    M.matvec(e, rhs)
    sys.stderr.write(' Factorizing matrix... ')
    solver = PyMa57Solver(M)
    w = sys.stderr.write
    w(' done\n')
    w(' Matrix order = %d\n' % solver.n)
    w(' Number of 2x2 pivots = %d\n' % solver.n2x2pivots)
    w(' Number of negative eigenvalues = %d\n' % solver.neig)
    w(' Matrix rank = %d\n' % solver.rank)
    w(' Matrix is rank deficient : %s\n' % repr(solver.isFullRank))
    w(' Solving system... ')
    solver.solve(rhs)
    w(' done\n')
    w(' Residual = %-g\n' % np.linalg.norm(solver.residual, ord=np.inf))
    w(' Relative error = %-g\n' % np.linalg.norm(solver.x - e, ord=np.inf))
    w(' Performing iterative refinement if necessary... ')
    solver.refine(rhs)
    w(' done\n')
    w(' Computed estimates:\n')
    w('   Condition number estimate: %8.1e\n' % solver.cond)
    w('   First backward error estimate: %8.1e\n' % solver.berr)
    w('   Second backward error estimate: %8.1e\n' % solver.berr2)
    w('   Direct error estimate: %8.1e\n' % solver.dirError)
    w('   Infinity-norm of input matrix: %8.1e\n' % solver.matNorm)
    w('   Infinity-norm of computed solution: %8.1e\n' % solver.xNorm)
    w('   Relative residual: %8.1e\n' % solver.relRes)
    # w(' Residual = %-g\n' % np.linalg.norm(solver.residual, ord=np.inf))
    w(' Relative error = %-g\n' % np.linalg.norm(solver.x - e, ord=np.inf))
