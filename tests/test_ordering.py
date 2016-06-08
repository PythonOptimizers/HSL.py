import numpy as np
from unittest import TestCase
import pytest

try:
    from hsl.ordering import _mc21
except ImportError:
    pass

try:
    from hsl.ordering import _mc60
except ImportError:
    pass


class TestMC21(TestCase):

    def setUp(self):
        pytest.importorskip("hsl.ordering._mc21")

    def test_spec_sheet(self):
        """Solve example from the spec sheet.

        Ordering
        http://www.hsl.rl.ac.uk/specs/mc21.pdf
        """
        n = 4
        icn = np.array([1, 4, 3, 4, 1, 4, 2, 4], dtype=np.int32)
        ip = np.array([1, 3, 5, 7], dtype=np.int32)
        lenr = np.array([2, 2, 2, 2], dtype=np.int32)
        iperm, numnz = _mc21.mc21ad(icn, ip, lenr)
        assert np.array_equal(iperm, np.array([1, 4, 2, 3]))


class TestMC60(TestCase):

    def setUp(self):
        pytest.importorskip("hsl.ordering._mc60")

    def test_spec_sheet(self):
        """Solve example from the spec sheet.

        Ordering
        http://www.hsl.rl.ac.uk/specs/mc60.pdf
        """
        icntl = np.array([0, 6], dtype=np.int32)  # Abort on error
        jcntl = np.array([0, 0], dtype=np.int32)  # Sloan's alg with auto choice
        weight = np.array([2, 1])                 # Weights in Sloan's alg

        # Store lower triangle of symmetric matrix in csr format (1-based)
        n = 5
        icptr = np.array([1, 6, 8, 9, 10, 11], dtype=np.int32)  # nnz = 10
        irn = np.empty(2 * (icptr[-1] - 1), dtype=np.int32)
        irn[:icptr[-1] - 1] = np.array([1, 2, 3,
                                        4, 5, 2, 3, 3, 4, 5], dtype=np.int32)

        # Check data
        info = _mc60.mc60ad(irn, icptr, icntl)

        # Compute supervariables
        nsup, svar, vars = _mc60.mc60bd(irn, icptr)
        assert nsup == 4
        print 'The number of supervariables is ', nsup

        # Permute reduced matrix
        permsv = np.empty(nsup, dtype=np.int32)
        pair = np.empty((2, nsup / 2), dtype=np.int32)
        info = _mc60.mc60cd(n, irn, icptr[:nsup + 1],
                            vars[:nsup], jcntl, permsv, weight, pair)

        # Compute profile and wavefront
        rinfo = _mc60.mc60fd(n, irn, icptr[:nsup + 1], vars[:nsup], permsv)

        # Obtain variable permutation from supervariable permutation
        perm, possv = _mc60.mc60dd(svar, vars[:nsup], permsv)

        assert np.array_equal(perm, np.array([3, 5, 4, 1, 2], np.int32))
        assert rinfo[0] == 10
