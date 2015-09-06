from libc.stdio cimport FILE
from cysparse.sparse.ll_mat_matrices.ll_mat_INT64_t_FLOAT64_t cimport LLSparseMatrix_INT64_t_FLOAT64_t
from cpython cimport Py_INCREF, Py_DECREF
from cpython.mem cimport PyMem_Malloc
cimport numpy as np
import numpy as np

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
    def __cinit__(self, LLSparseMatrix_INT64_t_FLOAT64_t A):
        cdef int elem, i, k

        self.A = A
        Py_INCREF(self.A)  # increase ref to object to avoid the user deleting it explicitly or implicitly

        assert A.ncol == A.nrow

        self.n = A.nrow
        nz = A.nnz

        print 'nnz: ', nz

        self.data = Ma57_Initialize(nz, self.n, NULL)

        #TODO: use pointer instead of copy
        self.a = <double *> PyMem_Malloc(nz * sizeof(double))

        # Set pivot-for-stability threshold is matrix is SQD */
        if True: # sqd
            self.data.cntl[0]  = 1.0e-15
            print self.data.cntl[0]
            self.data.cntl[1] = 1.0e-15;
            self.data.icntl[6] = 1;

        # Get matrix in coordinate format. Adjust indices to be 1-based.
        elem = 0;
        for i in xrange(self.n):
            k = A.root[i]
            while k != -1: 
                self.data.irn[elem] = i + 1
                self.data.jcn[elem] = A.col[k] + 1
                self.a[elem] = A.val[k] #TODO: use pointer instead of copy
                # print 'elem: %d, a[elem]: %f'%(elem, self.a[elem])
                k = A.link[k]
                elem += 1

        # Analyze
        self.analyze()
        return

    property factorized:
        def __get__(self): return self.factorized
    property cond:
        def __get__(self): return self.cond 

    def factorize(self, *args):
        """
        Perform numerical factorization. Before this can be done, symbolic
        factorization (the "analyze" phase) must have been performed.

        The values of the elements of the matrix may have been altered since
        the analyze phase but the sparsity pattern must not have changed. Use
        the optional argument newA to specify the updated matrix if applicable.
        """
        error = Ma57_Factorize(self.data, self.a)
        if error:
            raise RuntimeError("Error return code from Factorize: %-d\n", error)

        self.factorized = True

        # Find out if matrix was rank deficient
        self.data.rank = self.data.info[24]
        self.data.rankdef = True if (self.data.rank < self.data.n) else False
        print 'rankdef: ', self.data.rankdef
        return
    
    # TODO: add residual
    # WARNING: NLPy returns none and store solution in `self.x`
    def solve(self, np.ndarray[double, ndim=1] rhs, np.ndarray[double, ndim=1] residual,
              bint get_resid):
        """
        solve(b) solves the linear system of equations Ax = b.
        The solution will be found in self.x and residual in
        self.residual.
        """
        if rhs.size != self.n:
            raise ValueError("Right hand side has wrong size!\n"
                             "Attempting to solve the linear system, where A is of size (%d, %d) "
                             "and rhs is of size (%g)"%(self.n, self.n, rhs.size))

        x = rhs.copy() # x<- rhs ; will be overwritten
        self.data.residual  = <double *> np.PyArray_DATA(residual)

        error = Ma57_Solve(self.data, <double *> np.PyArray_DATA(x))

        if error:
            raise RuntimeError("Error return code from Solve: %-d\n", error)

        return x

    def refine(self, np.ndarray[double, ndim=1] x, np.ndarray[double, ndim=1] rhs, int nitref, *args):
        """
        refine( b, nitref ) performs iterative refinement if necessary
        until the scaled residual norm ||b-Ax||/(1+||b||) falls below the
        threshold 'tol' or until nitref steps are taken.
        Make sure you have called solve() with the same right-hand
        side b before calling refine().
        The residual vector self.residual will be updated to reflect
        the updated approximate solution.

        By default, nitref = 3.
        """

        x_0 = x.copy()
        rhs_0 = rhs.copy()
        error = Ma57_Refine(self.data, <double *> np.PyArray_DATA(x_0), <double *> np.PyArray_DATA(rhs_0), self.a, nitref, 2)

        print error

        self.cond     = self.data.rinfo[10]    # 1st cond number estimate
        self.cond2    = self.data.rinfo[11]    # 2nd cond number estimate 
        self.berr     = self.data.rinfo[5]     # 1st backward err estimate
        self.berr2    = self.data.rinfo[6]     # 2nd backward err estimate
        self.dirError = self.data.rinfo[12]    # direct error estimate
        self.matNorm  = self.data.rinfo[7]     # Inf-norm of input matrix
        self.xNorm    = self.data.rinfo[8]     # Inf-norm of solution
        self.relRes   = self.data.rinfo[9]     # Relative residual

        return (x_0, rhs_0)

    def analyze(self, *args):
        error = Ma57_Analyze(self.data)
        if error:
            raise RuntimeError("Error return code from Analyze: %-d\n", error)
        return

    def fetch_perm(self, *args):
        """
        fetch_perm() returns the permutation vector p used
        to compute the factorization of A. Rows and columns
        were permuted so that

              P^T  A P = L  B  L^T

        where i-th row of P is the p(i)-th row of the
        identity matrix, L is unit upper triangular and
        B is block diagonal with 1x1 and 2x2 blocks.
        """
        perm = []
        cdef int i
        for i in xrange(self.n):
            perm.append(self.data.keep[i])
        return perm

    def stats(self):
        """
        Return statistics on the solve
        """
        return (self.data.info[13], # number of entries in factors
                self.data.info[14], # storage for real data of factors
                self.data.info[15], # storage for int  data of factors
                self.data.info[20], # largest front size
                self.data.info[21], # number of 2x2 pivots
                self.data.info[23], # number of negative eigenvalues
                self.data.info[24]) # matrix rank

    def __dealloc__(self):
        return
