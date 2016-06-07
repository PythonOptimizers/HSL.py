"""Tests relative to MA27."""

import numpy as np
from unittest import TestCase
from pysparse import spmatrix
from pykrylov.linop import PysparseLinearOperator, IdentityOperator, linop_from_ndarray
import pytest
try:
    from hsl.solvers.pyma27 import PyMa27Solver
except ImportError:
    pass


def hilbert(n):
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


def ma27_spec_sheet():
    """This is the example from the MA27 spec sheet.

    Solution should be [1,2,3,4,5].
    """
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


class Test_MA27(TestCase):

    def setUp(self):
        pytest.importorskip("hsl.solvers._pyma27")

    def test_init(self):
        # Solve example from the spec sheet
        (A, rhs) = ma27_spec_sheet()
        sils = PyMa27Solver(A)
        assert sils.isFullRank is True
        assert np.array_equal(sils.x, np.zeros(5))

    def test_solve_spec_sheet(self):
        # Solve example from the spec sheet
        (A, rhs) = ma27_spec_sheet()
        sils = PyMa27Solver(A)
        sils.solve(rhs)
        assert np.allclose(sils.x, np.array([1., 2., 3., 4., 5.]))
        assert sils.inertia == (3, 2, 0)

    def test_solve_hilbert(self):
        # Solve example with Hilbert matrix
        n = 10
        H = hilbert(n)
        e = np.ones(n, 'd')
        rhs = np.empty(n, 'd')
        H.matvec(e, rhs)
        sils = PyMa27Solver(H)
        sils.solve(rhs)
        assert np.allclose(sils.x, e, 1e-3)
        sils.refine(rhs, niteref=5, tol=1e-18)
        assert np.allclose(sils.residual, np.zeros(n), 1e-18)

    # def test_fetch_lb_perm(self):
    #     """P^T  A P = L  B  L^T"""
    #     # Example from the spec sheet
    #     (A_sp, rhs) = ma27_spec_sheet()
    #     sils = PyMa27Solver(A_sp)
    #     perm = sils.fetch_perm()
    #     sils.fetch_lb()
    #     P = linop_from_ndarray(np.eye(5)[np.array(perm) - 1, :])
    #     A = PysparseLinearOperator(A_sp)
    #     L = PysparseLinearOperator(sils.L)
    #     B = PysparseLinearOperator(sils.B)
    #
    #     assert np.allclose((L * B * L.T).to_array(), (P.T * A * P).to_array())
