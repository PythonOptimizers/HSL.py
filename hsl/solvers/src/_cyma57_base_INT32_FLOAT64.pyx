from libc.stdio cimport FILE
from cpython.mem cimport PyMem_Malloc, PyMem_Free
cimport numpy as np
import numpy as np

cnp.import_array()

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


cdef c_to_fortran_index_array(int * a, int a_size):
    cdef:
        int i

    for i from 0 <= i < a_size:
        a[i] += 1


cdef class BaseMA57Solver_INT32_FLOAT64:
    def __cinit__(self, int m, int n, int nnz, bint sqd=False, verbose=False):
        cdef int elem, i, k

        assert m == n

        self.n = n
        self.nnz = nnz

        self.data = Ma57_Initialize(self.nnz, self.n, NULL)

        self.a = <double *> PyMem_Malloc(self.nnz * sizeof(double))

        # Set pivot-for-stability threshold if matrix is SQD
        if sqd:
            self.data.cntl[0]  = 1.0e-15
            print self.data.cntl[0]
            self.data.cntl[1] = 1.0e-15;
            self.data.icntl[6] = 1;

        return


    def __dealloc__(self):
        PyMem_Free(self.a)
        return

    cdef index_to_fortran(self):
        """
        Convert 0-based indices to Fortran indices (1-based).

        Note:
          Only for ``irn`` and ``jcn``.
        """

        # transform c index arrays to fortran arrays
        c_to_fortran_index_array(self.data.irn, self.nnz)
        c_to_fortran_index_array(self.data.jcn, self.nnz)


    property factorized:
        def __get__(self): return self.factorized
    property cond:
        def __get__(self): return self.cond

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
        return

    def solve(self, np.ndarray[double, ndim=1] rhs, bint get_resid):
        """
        solve(b) solves the linear system of equations Ax = b.
        The solution will be found in self.x and residual in
        self.residual.
        Warning: only one right-hand side is allowed.
        """
        if rhs.size != self.n:
            raise ValueError("Right hand side has wrong size!\n"
                             "Attempting to solve the linear system, where A is of size (%d, %d) "
                             "and rhs is of size (%g)"%(self.n, self.n, rhs.size))

        x = rhs.copy() # x<- rhs ; will be overwritten

        # When residual is requested, we need to call Refine instead of Solve
        if get_resid:
            residual = rhs.copy()
            self.data.residual = <double *> np.PyArray_DATA(residual)
            error = Ma57_Refine(self.data,
                                <double *> np.PyArray_DATA(x),
                                <double *> np.PyArray_DATA(rhs),
                                self.a,
                                1,
                                0)
            if error:
                raise RuntimeError("Error return code from Solve: %-d\n", error)
    
            return (x, residual)

        else: 
            error = Ma57_Solve(self.data, <double *> np.PyArray_DATA(x))
            if error:
                raise RuntimeError("Error return code from Solve: %-d\n", error)
            return x


    def refine(self, np.ndarray[double, ndim=1] x, np.ndarray[double, ndim=1] rhs,
               np.ndarray[double, ndim=1] residual, int nitref=3, *args):
        """
        refine performs iterative refinement if necessary
        until the scaled residual norm ||b-Ax||/(1+||b||) falls below a threshold 'tol'
        or until nitref steps are taken.
        
        warning: Make sure you have called solve() with the same right-hand
        side b before calling refine().

        Args:
            x: an estimated solution of Ax = b
            rhs: right-hand side
            residual: residual associated with given x entry
            nitref: max number of iterative refinement steps

        Returns:
            (tuple):
                * new_x: improved solution vector
                * new_res: last residual vector
        """

        new_x = x.copy()
        new_res = residual.copy()
        self.data.residual = <double *> np.PyArray_DATA(new_res)

        error = Ma57_Refine(self.data,
                            <double *> np.PyArray_DATA(new_x),
                            <double *> np.PyArray_DATA(rhs),
                            self.a,
                            nitref,
                            2)
        if error:
            raise RuntimeError("Error return code from Refine: %-d\n", error)

        self.cond     = self.data.rinfo[10]    # 1st cond number estimate
        self.cond2    = self.data.rinfo[11]    # 2nd cond number estimate
        self.berr     = self.data.rinfo[5]     # 1st backward err estimate
        self.berr2    = self.data.rinfo[6]     # 2nd backward err estimate
        self.dirError = self.data.rinfo[12]    # direct error estimate
        self.matNorm  = self.data.rinfo[7]     # Inf-norm of input matrix
        self.xNorm    = self.data.rinfo[8]     # Inf-norm of solution
        self.relRes   = self.data.rinfo[9]     # Relative residual

        return (new_x, new_res)

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