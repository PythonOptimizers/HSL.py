from libc.stdio cimport FILE
from cysparse.sparse.ll_mat_matrices.ll_mat_INT64_t_FLOAT64_t cimport LLSparseMatrix_INT64_t_FLOAT64_t
from cpython cimport Py_INCREF, Py_DECREF
cimport numpy as np

cdef extern from "ma57.h":
    ctypedef struct Ma57_Data:
        int       n, nz               # Order and #nonzeros
        int       icntl[20]
        int       info[40]
        double    cntl[5]
        double    rinfo[20]
        int      *irn                 # Sparsity pattern    
        int      *jcn
        int       lkeep               # Pivot sequence      
        int      *keep               
        int      *iwork               # Wokspace array      
        double   *fact                # Matrix factors      
        int       lfact               # Size of array fact  
        int      *ifact               # Indexing of factors 
        int       lifact              # Size of array ifact 
        int       job
        int       nrhs                # Number of rhs       
        double   *rhs                 # Right-hand sides    
        int       lrhs                # Leading dim of rhs  
        double   *work                # Real workspace      
        int       lwork               # Size of array work  
        int       calledcd            # Flag for MA57DD     
        double   *x                   # Solution to Ax=rhs  
        double   *residual            # = A x - rhs         
        char      fetched             # Factors were fetched
                                      # Used for de-allocation
        int       rank, rankdef
        FILE     *logfile             # File for log output 

    cdef Ma57_Data *Ma57_Initialize( int nz, int n, FILE *logfile )
    cdef int  Ma57_Analyze( Ma57_Data *ma57 );
    cdef int  Ma57_Factorize( Ma57_Data *ma57, double A[] );
    cdef int  Ma57_Solve( Ma57_Data *ma57, double x[] );
    cdef int  Ma57_Refine( Ma57_Data *ma57, double x[], double rhs[], double A[],
                           int maxitref, int job );
    cdef void Ma57_Finalize(      Ma57_Data *ma57 );
    cdef int  Process_Error_Code( Ma57_Data *ma57, int nerror );


#cdef populate_ma57_struct_from_cysparse_llmat(LLSparseMatrix_INT64_t_FLOAT64_t A):


cdef class MA57Context:
    cdef:
        LLSparseMatrix_INT64_t_FLOAT64_t A
        int n
        int nz
        Ma57_Data* data
        double* a
        np.ndarray residual
        int factorized
        double cond
        double cond2
        double berr
        double berr2
        double dirError
        double matNorm
        double xNorm
        double relRes


