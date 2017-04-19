from hsl.solvers.src._cyma57_base_INT32_FLOAT64 cimport BaseMA57Solver_INT32_FLOAT64

cimport numpy as cnp

cdef class NumpyMA57Solver_INT32_FLOAT64(BaseMA57Solver_INT32_FLOAT64):
    cpdef get_matrix_data(self, cnp.ndarray[cnp.int32_t, ndim=1] arow,
                                cnp.ndarray[cnp.int32_t, ndim=1] acol,
                                cnp.ndarray[cnp.float64_t, ndim=1] aval)