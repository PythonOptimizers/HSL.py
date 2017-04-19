from libc.stdint cimport int64_t
from libc.string cimport strncpy, memcpy

import numpy as np
cimport numpy as cnp

cnp.import_array()

from libc.stdio cimport FILE
cimport numpy as np

cdef extern from "ma27.h":
    ctypedef struct Ma27_Data:
        int       n, nz               # Order and #nonzeros
        int       icntl[30]
        int       info[20]
        double    cntl[5]
        int      *irn                 # Sparsity pattern
        int      *icn
        int      *iw                  # Integer workspace
        int       liw
        int      *ikeep               # Pivot sequence
        int      *iw1                 # Integer workspace
        int       nsteps
        int       iflag               # Pivot selection
        double    ops                 # Operation count
    
        char      rankdef             # Indicate whether matrix is rank-deficient
        int       rank;               # Matrix rank
    
        int       la
        double   *factors             # Matrix factors
        int       maxfrt
        double   *w                   # Real workspace
    
        double   *residual            # = b - Ax   
        char      fetched             # Factors have been fetched
                                      # Used for de-allocation

        FILE     *logfile             # File for log output

    cdef Ma27_Data *Ma27_Initialize( int nz, int n, FILE *logfile )
    cdef int  Ma27_Analyze( Ma27_Data *ma27, int iflag );
    cdef int  Ma27_Factorize( Ma27_Data *ma27, double A[] );
    cdef int  Ma27_Solve( Ma27_Data *ma27, double x[] );
    cdef int  Ma27_Refine( Ma27_Data *ma27, double x[], double rhs[], double A[],
                           double tol, int maxitref );
    cdef void Ma27_Finalize( Ma27_Data *ma27 );
    cdef int  Process_Error_Code( Ma27_Data *ma27, int error );


cdef class BaseMA27Solver_INT32_FLOAT64:
    cdef:
        int n
        int nnz
        Ma27_Data* data
        double* a
        int factorized

    cdef index_to_fortran(self)
