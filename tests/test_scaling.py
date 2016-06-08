import numpy as np
from unittest import TestCase
import pytest

try:
    from hsl.scaling.mc29 import MC29AD_scale, unscale
except ImportError:
    pass


class TestMC29(TestCase):

    def setUp(self):
        pytest.importorskip("hsl.scaling._mc29")

    def test_init(self):
        """Solve example from the spec sheet.

        In-place scaling.
        http://www.hsl.rl.ac.uk/specs/mc29.pdf
        """
        irow = np.array([3, 0, 3, 1, 2, 2], dtype=np.int32)
        jcol = np.array([2, 0, 1, 1, 0, 2], dtype=np.int32)
        values = np.array([16000, 100, 14000, 6, 900, 110000], dtype=np.float64)

        # Obtain row and column scaling
        val = values.copy()
        row_scale, col_scale = MC29AD_scale(4, 3, irow, jcol, val)
        assert np.allclose(val, np.array(
            [0.8790, 1.8123, 1.2811, 0.7806, 0.5518, 1.1377]), 1e-4)

        unscale(4, 3, row_scale, col_scale, irow, jcol, val)
        assert np.allclose(val, values)
