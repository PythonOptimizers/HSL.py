from libc.stdio cimport FILE
from cpython.mem cimport PyMem_Malloc, PyMem_Free
cimport numpy as np
import numpy as np

cnp.import_array()

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


cdef c_to_fortran_index_array(int * a, int a_size):
    cdef:
        int i

    for i from 0 <= i < a_size:
        a[i] += 1


cdef class BaseMA27Solver_INT32_FLOAT64:
    def __cinit__(self, int m, int n, int nnz, bint sqd=False, verbose=False):
        assert m == n

        self.n = n
        self.nnz = nnz

        self.data = Ma27_Initialize(self.nnz, self.n, NULL)

        self.a = <double *> PyMem_Malloc(self.nnz * sizeof(double))

        # Set pivot-for-stability threshold if matrix is SQD
        if sqd:
            self.data.cntl[0]  = 1.0e-15

        return


    def __dealloc__(self):
        PyMem_Free(self.a)
        return

    cdef index_to_fortran(self):
        """
        Convert 0-based indices to Fortran indices (1-based).

        Note:
          Only for ``irn`` and ``icn``.
        """

        # transform c index arrays to fortran arrays
        c_to_fortran_index_array(self.data.irn, self.nnz)
        c_to_fortran_index_array(self.data.icn, self.nnz)


    property factorized:
        def __get__(self): return self.factorized

    def analyze(self, *args):
        error = Ma27_Analyze(self.data, 0)  # iflag = 0: automatic pivot choice
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
            perm.append(self.data.ikeep[i])
        return perm

    def factorize(self, *args):
        """
        Perform numerical factorization. Before this can be done, symbolic
        factorization (the "analyze" phase) must have been performed.

        The values of the elements of the matrix may have been altered since
        the analyze phase but the sparsity pattern must not have changed. Use
        the optional argument newA to specify the updated matrix if applicable.
        """
        error = Ma27_Factorize(self.data, self.a)
        if error:
            raise RuntimeError("Error return code from Factorize: %-d\n", error)

        self.factorized = True

        # Find out if matrix was rank deficient
        self.data.rankdef = False
        if (self.data.info[0] == 3 or self.data.info[0] == -5):
            self.data.rankdef =  True
            self.data.rank = self.data.info[1]
        return

    def solve(self, np.ndarray[double, ndim=1] rhs, bint get_resid):
        """
        solve(b) solves the linear system of equations Ax = b.
        The solution will be found in self.x and residual in
        self.residual.
        Warning: only one right-hand side is allowed.
        """
        cdef i,j,k
        if rhs.size != self.n:
            raise ValueError("Right hand side has wrong size!\n"
                             "Attempting to solve the linear system, where A is of size (%d, %d) "
                             "and rhs is of size (%g)"%(self.n, self.n, rhs.size))

        x = rhs.copy() # x<- rhs ; will be overwritten
        error = Ma27_Solve(self.data, <double *> np.PyArray_DATA(x))
        if error:
            raise RuntimeError("Error return code from Solve: %-d\n", error)

        # When residual is requested, compute r = rhs - Ax
        if get_resid:
            residual = rhs.copy()
            self.data.residual = <double *> np.PyArray_DATA(residual)
            for k in xrange(self.data.nz):
                i = self.data.irn[k] - 1  # Fortran indexing
                j = self.data.icn[k] - 1
                self.data.residual[i] -= self.a[k] * x[j]
                if i != j:
                    self.data.residual[j] -= self.a[k] * x[i]

            return (x, residual)
        else:
            return x


    def refine(self, np.ndarray[double, ndim=1] x, np.ndarray[double, ndim=1] rhs,
               np.ndarray[double, ndim=1] residual, double tol=1e-8, int nitref=3, *args):
        """Perform iterative refinement.

        If necessary, it performs iterative refinement until the scaled
        residual norm ||b-Ax||/(1+||b||) falls below a threshold 'tol' or until
        nitref steps are taken.

        warning: Make sure you have called solve() with the same right-hand
        side b before calling refine().

        Args:
            x: an estimated solution of Ax = b
            rhs: right-hand side
            residual: residual associated with given x entry
            tol: threshold for the scaled residual norm
            nitref: max number of iterative refinement steps

        Returns:
            (tuple):
                * new_x: improved solution vector
                * new_res: last residual vector
        """

        new_x = x.copy()
        new_res = residual.copy()

        self.data.residual = <double *> np.PyArray_DATA(new_res)

        error = Ma27_Refine(self.data,
                            <double *> np.PyArray_DATA(new_x),
                            <double *> np.PyArray_DATA(rhs),
                            self.a,
                            tol,
                            nitref)

        if error:
            raise RuntimeError("Error return code from Refine: %-d\n", error)

        return (new_x, new_res)

    def stats(self):
        """Return statistics on the solve."""
        return (self.data.info[8],  # storage for real data of factors
                self.data.info[9],  # storage for int  data of factors
                self.data.info[10], # nb of data compresses performed in analysis
                self.data.info[11], # nb of real compresses performed in analysis
                self.data.info[12], # nb of int compresses performed in analysis
                self.data.info[13], # number of 2x2 pivots
                self.data.info[14], # number of negative eigenvalues
                self.data.rank)     # matrix rank