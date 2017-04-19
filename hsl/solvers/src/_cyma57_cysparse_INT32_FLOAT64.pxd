from cysparse.sparse.ll_mat_matrices.ll_mat_INT32_t_FLOAT64_t cimport LLSparseMatrix_INT32_t_FLOAT64_t

from hsl.solvers.src._cyma57_base_INT32_FLOAT64 cimport BaseMA57Solver_INT32_FLOAT64

cdef class CySparseMA57Solver_INT32_FLOAT64(BaseMA57Solver_INT32_FLOAT64):
    cpdef get_matrix_data(self, LLSparseMatrix_INT32_t_FLOAT64_t A)