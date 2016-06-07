# Matrix scaling module.

from hsl.scaling._mc29 import mc29ad
import numpy as np


def MC29AD_scale(m, n, a_row, a_col, a_val, b=None):
    """Use MC29AD for scaling values of A (in place).

    Matrix A to scale must be provided in coordinate format

    :parameters:
        :m: number of rows of A
        :n: number of columns of A
        :a_row: row indices of non zero elements of A
        :a_col: column indices of non zero elements of A
        :a_val: values of non zeros elements of A (in/out)
        :b: right-hand side (optional)

    Returns:
        (tuple):
            * row_scale: row scaling factors
            * col_scale: column scaling factors
    """
    # Obtain row and column scaling
    # We need to add one to row and column indices to comply to Fortran
    # format.
    row_scale, col_scale, ifail = mc29ad(m, n, a_val, a_row + 1, a_col + 1)

    if ifail == -1:
        raise ValueError("Number of rows < 1 or number of columns < 1")
    elif ifail == -2:
        raise ValueError("Number of non zero elements < 1")

    # row_scale and col_scale contain in fact the logarithms of the
    # scaling factors.
    row_scale = np.exp(row_scale)
    col_scale = np.exp(col_scale)

    # Apply row and column scaling to constraint matrix A.
    a_val *= row_scale[a_row]
    a_val *= col_scale[a_col]

    if b is not None:
        # Apply row scaling to right-hand side b.
        b *= row_scale

    return (row_scale, col_scale)


def unscale(m, n, row_scale, col_scale, a_row, a_col, a_val, b=None):
    """Unscale values of A and possibly right-hand side.

    Unscaling is performed using user-provided row and column scaling factors.

    Matrix A to scale must be provided in coordinate format

    :parameters:
        :m: number of rows of A
        :n: number of columns of A
        :row_scale: row scaling factors
        :col_scale: column scaling factors
        :a_row: row indices of non zero elements of A
        :a_col: column indices of non zero elements of A
        :a_val: values of non zeros elements of A (in/out)
        :b: right-hand side (optional)
    """
    # Unscale values of matrix A.
    a_val /= row_scale[a_row]
    a_val /= col_scale[a_col]

    if b is not None:
        # Unscale right-hand side b.
        b /= row_scale

    return
