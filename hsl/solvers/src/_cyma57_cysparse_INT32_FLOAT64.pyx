from cysparse.sparse.ll_mat_matrices.ll_mat_INT32_t_FLOAT64_t cimport LLSparseMatrix_INT32_t_FLOAT64_t

from hsl.solvers.src._cyma57_base_INT32_FLOAT64 cimport BaseMA57Solver_INT32_FLOAT64


cdef class CySparseMA57Solver_INT32_FLOAT64(BaseMA57Solver_INT32_FLOAT64):
    """
    MA57 Context.

    This version **only** deals with ``LLSparseMatrix_INT32_t_FLOAT64_t`` objects.

    A: A :class:`LLSparseMatrix_INT32_t_FLOAT64_t` object.

    Warning:
        The solver takes a "snapshot" of the matrix ``A``, i.e. the results given by the solver are only
        valid for the matrix given. If the matrix ``A`` changes aferwards, the results given by the solver won't
        reflect this change.

    """

    def __cinit__(self, int m, int n, int nnz, bint sqd=False, verbose=False):
        pass

    cpdef get_matrix_data(self, LLSparseMatrix_INT32_t_FLOAT64_t A):
        """
        Args:
            A: :class:`LLSparseMatrix_INT32_t_FLOAT64_t` object.

        Note: we keep the same name for this method in all derived classes.
        """
        # Memory allocation of `irn`, `jcn` and `a` is done by `BaseMA57Solver`.

        A.fill_triplet(self.data.irn, self.data.jcn, self.a)

        # convert irn and jcn indices to Fortran format
        self.index_to_fortran()
