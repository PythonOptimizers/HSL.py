from hsl.solvers.src._cyma57_base_INT32_FLOAT64 cimport BaseMA57Solver_INT32_FLOAT64

from libc.string cimport memcpy

cimport numpy as cnp
cnp.import_array()

cdef class NumpyMA57Solver_INT32_FLOAT64(BaseMA57Solver_INT32_FLOAT64):
    """
    MA57 Context.

    This version **only** deals with matrices supplied in coordinate format through Numpy arrays.


    """

    def __cinit__(self, int m, int n, int nnz, bint sqd=False, verbose=False):
        pass

    cpdef get_matrix_data(self, cnp.ndarray[cnp.int32_t, ndim=1] arow,
                                cnp.ndarray[cnp.int32_t, ndim=1] acol,
                                cnp.ndarray[cnp.float64_t, ndim=1] aval):
        """
        Args:
            a_row: row indices of non zero elements of A
            a_col: column indices of non zero elements of A
            a_val: values of non zeros elements of A

        Note: we keep the same name for this method in all derived classes.
        """
        # Memory allocation of `irn`, `jcn` and `a` is done by `BaseMA57Solver`.
        memcpy(self.data.irn, <int *> cnp.PyArray_DATA(arow), self.nnz*sizeof(int))
        memcpy(self.data.jcn, <int *> cnp.PyArray_DATA(acol), self.nnz*sizeof(int))
        memcpy(self.a, <int *> cnp.PyArray_DATA(aval), self.nnz*sizeof(double))


        # convert irn and jcn indices to Fortran format
        self.index_to_fortran()