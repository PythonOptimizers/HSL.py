"""Harwell-Boeing and Rutherford-Boeing matrix format reader.

Provides access to sparse linear systems described in Harwell-Boeing or
Rutherford-Boeing format. This module exposes the two classes
HarwellBoeingMatrix and RutherfordBoeingData. For more information, see
the references below.

**References**

.. [DGL] I.S. Duff, R.G. Grimes and J.G. Lewis,
         Sparse Matrix Test Problems, ACM Transactions on
         Mathematical Software, 15(1), p.1-14, 1989

.. [HBUG] `<ftp://ftp.cerfacs.fr/pub/algo/matrices/harwell_boeing/userguide.ps.Z>`_

.. [HB] `<http://math.nist.gov/MatrixMarket/data/Harwell-Boeing>`_

.. [RBC] The Rutherford-Boeing Sparse Matrix Collection,
        I.S. Duff, R.G. Grimes and J.G. Lewis, Technical Report RAL-TR-97-031,
        Rutherford Appleton Laboratory, Chilton, OX, UK, 1997.
        (`<ftp://ftp.numerical.rl.ac.uk/pub/reports/duglRAL97031.pdf>`_)

.. [RB] `<http://www.cerfacs.fr/algor/Softs/RB>`_

.. moduleauthor:: dominique.orban@gerad.ca
"""
import numpy as np
from fortranformat import FortranRecordReader, FortranRecordWriter
from fortranformat import config as ff_config
from conversion import csc2coord, coord2csc

# Possibility to set ff_config.RET_WRITTEN_VARS_ONLY = True
# See:
# https://bitbucket.org/brendanarnold/py-fortranformat/issue/1/reading-less-records-than-specified-by#comment-531697


class HarwellBoeingMatrix(object):
    """Import a sparse matrix from a file in Harwell-Boeing format.

    The matrix is stored in compressed sparse row format in (self.ind, self.ip,
    self.val). Right-hand sides, if any, are stored in self.rhs. Right-hand
    sides can be stored as dense vectors, in which case self.rhs has shape
    (nrow, nrhs), as sparse vectors, in which case they are stored in
    compressed sparse column format in (self.rhsptr, self.rhsind, self.rhs), or
    in elemental format (typically when the matrix itself is stored in
    finite-element format), in which case self.rhs has shape (nnzero, nrhs).

    Note that the matrix indices are zero-based, i.e., row indices range
    from 0 through nrow-1 and column indices range from 0 through ncol-1.

    The matrix can be subsequently converted to triple format with
        (val, row, col) = self.find()

    :keywords:

        :pattern_only:  do not read matrix element values (False)
        :read_rhs:      read right-hand sides, if any (False)
        :read_guess:    read starting guess, if any (False)
        :realSol:      read solution vector, if any (False)
    """

    def __init__(self, fname, **kwargs):

        self.title = ''
        self.key = ''
        self.ip = self.ind = self.val = None
        self.nrhs = 0
        self.rhsptr = self.rhsind = self.rhs = None
        self.guess = self.sol = None

        fp = open(fname, 'r')
        self._read_matrix(fp, **kwargs)
        fp.close()

    def data(self):
        """
        Return matrix data in compressed sparse row format.

        :returns:
            :val:   array of values of nonzero elements
            :ip:    array of pointer to rows
            :ind:   array of indices of nonzero elements in each row
        """
        # if self.ip is None or self.ind is None: return (None,None,None)
        return (self.val, self.ip, self.ind)

    def find(self):
        """
        Return matrix data in coordinate format.

        :returns:
            :val:   array of values of nonzero elements
            :irow:   array of indices of nonzero elements in each row
            :jcol:   array of indices of nonzero elements in each column
        """
        if self.ip is None or self.ind is None:
            return (None, None, None)
        irow, jcol = csc2coord(self.ind, self.ip)
        return (self.val, irow, jcol)

    def _read_array(self, fp, which, nelm, format):
        # print 'Reading %d values with format %s' % (nelm, format)
        fmt = FortranRecordReader(format)
        ind = 0
        while ind < nelm - 1:
            fdata = fmt.read(fp.readline())
            ind2 = min(ind + len(fdata), nelm)
            which[ind:ind2] = fdata[:ind2 - ind]
            ind = ind2
        # Read last line, if any.
        if ind < nelm:
            fdata = fmt.read(fp.readline())
            which[ind:] = fdata[:nelm - ind]
        return

    def _fortran_read(self, stream, format):
        fmt = FortranRecordReader(format)
        fdata = fmt.read(stream)
        return fdata

    def _read_matrix(self, fp, **kwargs):
        self.pattern_only = kwargs.get('pattern_only', False)
        self.read_rhs = kwargs.get('read_rhs', False)
        self.read_guess = kwargs.get('read_guess', False)
        self.read_sol = kwargs.get('read_sol', False)
        f_read = self._fortran_read

        # Read matrix header
        fp.seek(0)
        (self.title, self.key) = f_read(fp.readline(), 'A72,A8')
        (totcrd, ptrcdr, indcrd, valcrd, rhscrd) = f_read(fp.readline(), '5I14')
        (self.mxtype, self.nrow, self.ncol, self.nnzero, neltvl) = \
            f_read(fp.readline(), 'A3,11X,4I14')
        (ptrfmt, indfmt, valfmt, rhsfmt) = f_read(fp.readline(), '2A16,2A20')
        self.shape = (self.nrow, self.ncol)

        # Decide whether matrix is symmetric and real or complex
        data_type = np.float
        if self.mxtype[0] == 'C':
            data_type = np.complex
        self.issym = (self.mxtype[1] == 'S')

        # Read right-hand side info if present
        if rhscrd > 0:
            (rhstyp, self.nrhs, nrhsix) = f_read(fp.readline(), 'A3,11X,2I14')

        # Set up arrays to hold matrix pattern
        self.ip = np.empty(self.ncol + 1, dtype=np.int)
        self.ind = np.empty(self.nnzero, dtype=np.int)

        # Read matrix pattern
        self._read_array(fp, self.ip, self.ncol + 1, ptrfmt)
        self._read_array(fp, self.ind, self.nnzero, indfmt)

        # Adjust indices to be 0-based
        self.ip -= 1
        self.ind -= 1

        if self.pattern_only or self.mxtype[0] == 'P':
            return

        # Read matrix values
        if self.mxtype[2] == 'A':  # Matrix is assembled
            vallen = self.nnzero
        else:                     # Finite-element format, not assembled
            vallen = neltvl

        self.val = np.empty(vallen, dtype=data_type)
        self._read_array(fp, self.val, vallen, valfmt)

        # Read right-hand sides, if any
        if not self.read_rhs or self.nrhs == 0:
            return
        if rhstyp[0] == 'F':
            # Read dense right-hand sides
            self.rhs = np.empty((self.nrow, self.nrhs), data_type)
            for i in range(self.nrhs):
                self._read_array(fp, self.rhs[:, i], self.nrow, rhsfmt)
        elif self.mxtype[2] == 'A':
            # Read sparse right-hand sides
            self.rhsptr = np.empty(self.nrhs + 1, np.int)
            self.rhsind = np.empty(self.nrhsix, np.int)
            self.rhs = np.empty(self.nrhsix, data_type)
            self._read_array(fp, self.rhsptr, self.nrhs + 1, ptrfmt)
            self._read_array(fp, self.rhsind, self.nrhsix, indfmt)
            self._read_array(fp, self.rhs,    self.nrhsix, rhsfmt)
            self.rhsind -= 1
            self.rhsptr -= 1
        else:
            # Read elemental right-hand sides
            self.rhs = np.empty((self.nnzero, self.nrhs), data_type)
            for i in range(self.nrhs):
                self._read_array(fp, self.rhs[:, i], self.nnzero, rhsfmt)

        # Read initial guesses if requested (always dense)
        if self.read_guess and rhstyp[1] == 'G':
            self.guess = np.empty((self.nrow, self.nrhs), data_type)
            for i in range(self.nrhs):
                self._read_array(fp, self.guess[:, i], self.nrow, rhsfmt)

        # Read solution vectors if requested (always dense)
        if self.read_sol and rhstyp[2] == 'X':
            self.sol = np.empty((self.nrow, self.nrhs), data_type)
            for i in range(self.nrhs):
                self._read_array(fp, self.sol[:, i], self.nrow, rhsfmt)

        return


class RutherfordBoeingData(HarwellBoeingMatrix):
    """Imports data from a file in Rutherford-Boeing format.

    The data is held in (self.ind, self.ip, self.val). If the data represents a
    sparse matrix, the three arrays represent the matrix stored in compressed
    sparse row format. Otherwise, the three arrays represent the supplementary
    data. Refer to the Rutherford-Boeing documentation for more information
    (reference [4] in the docstring for the present module.)

    Note that the matrix indices are zero-based, i.e., row indices range from
    0 through nrow-1 and column indices range from 0 through ncol-1.

    The data can be subsequently converted to triple format with
        (val, row, col) = self.find()

    :keywords:

        :pattern_only:  do not read data values (False)
        :transposed:
    """

    def __init__(self, fname, **kwargs):

        HarwellBoeingMatrix.__init__(self, fname, **kwargs)
        self.transposed = kwargs.get('transposed', False)

    def _read_matrix(self, fp, **kwargs):
        self.pattern_only = kwargs.get('pattern_only', False)
        f_read = self._fortran_read

        # Read matrix header
        fp.seek(0)
        (self.title, self.key) = f_read(fp.readline(), 'A72,A8')
        (buffer1,) = f_read(fp.readline(), 'A80')
        (buffer2,) = f_read(fp.readline(), 'A80')

        self.issym = False

        if buffer2[2] in ['a', 'e']:
            (self.mxtype, self.m, self.nvec, self.ne, self.neltvl) = \
                f_read(buffer2, 'A3,11X,4(1X,I13)')

            self.nrow = self.m
            self.ncol = self.nvec
            self.shape = (self.nrow, self.ncol)
            self.nnzero = self.ne
            self.issym = (self.mxtype[1] == 's')
            data_type = np.float
            if self.mxtype[0] == 'c':
                data_type = np.complex
            elif self.mxtype[0] == 'i':
                data_type = np.int

            (ptrfmt, indfmt, valfmt) = f_read(fp.readline(), '2A16,A20')

            np1 = self.nvec + 1
            if self.mxtype[1:2] == 're':
                np1 = 2 * self.nvec + 1
            self.ip = np.empty(np1, np.int)
            self._read_array(fp, self.ip, np1, ptrfmt)

            self.ind = np.empty(self.ne, np.int)
            self._read_array(fp, self.ind, self.ne, indfmt)

            # Adjust indices to be 0-based
            self.ip -= 1
            self.ind -= 1

            # Stop here if pattern only is requested/available
            if self.pattern_only or self.mxtype[0] == 'p' or self.mxtype[0] == 'x':
                return

            # Read values
            nreal = self.ne
            if self.neltvl > 0:
                nreal = self.neltvl
            self.val = np.empty(nreal, dtype=data_type)
            self._read_array(fp, self.val, nreal, valfmt)

        else:

            # Read supplementary data
            (self.dattyp, self.positn, self.orgniz, self.caseid, numerf, m,
             nvec, self.nauxd) = f_read(buffer1,
                                        'A3,2A1,1X,A8,2X,A1,3(2X,I13)')
            auxfm1, auxfm2, auxfm3 = f_read(buffer2, '3A20')
            self.nrow = m
            self.nvec = self.ncol = nvec

            # Read integer data
            if (self.dattyp == 'rhs' and self.orgniz == 's') or \
                    self.dattyp in ['ipt', 'icv', 'ord']:
                if self.dattyp == 'ord':
                    self.nauxd = m * nvec
                    auxfm = auxfm1
                else:
                    self.ip = np.empty(nvec + 1, np.int)
                    self._read_array(fp, self.ip, nvec + 1, auxfm1)
                    auxfm = auxfm2
                    self.ip -= 1  # Adjust to 0-based indexing
                self.ind = np.empty(self.nauxd, np.int)
                self._read_array(fp, self.ind, self.nauxd, auxfm)
                self.ind -= 1  # Adjust to 0-based indexing
                if self.dattyp != 'rhs':
                    return

            if self.pattern_only:
                return

            # Read values
            data_type = np.float
            if numerf == 'c':
                data_type = np.complex
            elif numerf == 'i':
                data_type = np.int
            if self.dattyp != 'rhs':
                self.nauxd = m * nvec
            if self.dattyp == 'rhs' and self.orgniz == 's':
                auxfm = auxfm3
            else:
                auxfm = auxfm1
            self.val = np.empty(self.nauxd, data_type)
            self._read_array(fp, self.val, self.nauxd, auxfm)
            self.nnzero = self.nauxd

        return

    def _mul(self, other):
        # No type or dimension checking for now...
        y = np.zeros(self.nrow)
        for col in range(self.ncol):
            for k in range(self.ip[col], self.ip[col + 1]):
                row = self.ind[k]
                val = self.val[k]
                y[row] += val * other[col]
                if self.issym and row != col:
                    y[col] += val * other[row]
        return y

    def _rmul(self, other):
        # No type or dimension checking for now...
        y = np.zeros(self.ncol)
        for col in range(self.ncol):
            for k in range(self.ip[col], self.ip[col + 1]):
                row = self.ind[k]
                val = self.val[k]
                y[col] += val * other[row]
                if self.issym and row != col:
                    y[row] += val * other[col]
        return y

    def __mul__(self, other):
        if self.transposed:
            return self._rmul(other)
        else:
            return self._mul(other)


# Helper functions.

def get_int_fmt(n):
    """Return appropriate format for integer arrays."""
    fmts = ['(40I2)', '(26I3)', '(20I4)', '(16I5)', '(13I6)', '(11I7)',
            '(10I8)', '(8I9)', '(8I10)', '(7I11)', '(4I20)']
    nlines = [40, 26, 20, 16, 13, 11, 10, 8, 8, 7, 4]
    nn = n
    for k in range(1, n + 1):
        if nn < 10:
            break
        nn /= 10
    if k <= 10:
        return (fmts[k + 1], nlines[k + 1])
    return (fmts[10], nlines[10])


def get_real_fmt(p):
    """Return appropriate format for real array (1 <= p <= 17)."""
    fmt = ['(8E10.1E3)', '(7E11.2E3)', '(6E12.3E3)', '(6E13.4E3)',
           '(5E14.5E3)', '(5E15.6E3)', '(5E16.7E3)', '(4E17.8E3)',
           '(4E18.9E3)', '(4E19.10E3)', '(4E20.11E3)', '(3E21.12E3)',
           '(3E22.13E3)', '(3E23.14E3)', '(3E24.15E3)', '(3E25.16E3)']
    fmt1 = ['(1P,8E10.1E3)', '(1P,7E11.2E3)', '(1P,6E12.3E3)',
            '(1P,6E13.4E3)', '(1P,5E14.5E3)', '(1P,5E15.6E3)',
            '(1P,5E16.7E3)', '(1P,4E17.8E3)', '(1P,4E18.9E3)',
            '(1P,4E19.10E3)', '(1P,4E20.11E3)', '(1P,3E21.12E3)',
            '(1P,3E22.13E3)', '(1P,3E23.14E3)', '(1P,3E24.15E3)',
            '(1P,3E25.16E3)']
    lens = [8, 7, 6, 6, 5, 5, 5, 4, 4, 4, 4, 3, 3, 3, 3, 3]
    return (fmt[p - 2], fmt1[p - 2], lens[p - 2])


def fortran_write_line(data, stream, fformat):
    """Write `data` to `stream` according to Fortran format `fformat`."""
    fmt = FortranRecordWriter(fformat)
    stream.write(fmt.write(data))
    stream.write('\n')
    return


def fortran_write_array(data, chunk_size, stream, fformat):
    """Write data according to Fortran format.

    Write array `data` to `stream`, possibly using multiple lines,
    according to Fortran format `fformat`.
    """
    nelts = len(data)
    nelts_per_line = nelts / chunk_size
    # print 'Writing %d elements %d per line...' % (nelts, chunk_size)
    for k in range(nelts_per_line):
        chunk = data[k * chunk_size:(k + 1) * chunk_size]
        fortran_write_line(chunk, stream, fformat)
    if nelts_per_line * chunk_size < nelts:
        fortran_write_line(data[nelts_per_line * chunk_size:], stream, fformat)
    return

# End of helper functions.


def write_rb(fname, nrow, ncol, ip, ind,
             val=None, precision=17, symmetric=False, skew=False,
             title='Generic', key='Generic'):
    """Write a sparse matrix to file in Rutherford-Boeing format.

    The input matrix must be described in compressed column format by the
    arrays `ip` and `ind`. Rows must be ordered in each column.
    If numerical values are to be written to file, they should be specified in
    the array `val`.

    Currently only supports assembled matrices in compressed column format.
    """

    pattern_only = (val == None)
    rectangular = (nrow != ncol)
    ne = len(ind)

    # Check that columns are in order.
    # for j in range(ncol):
    #    if ip[j+1] <= ip[j]:
    #        raise ValueError, 'Columns must be ordered.'

    # Check that rows are in order in each column.
    # for j in range(ncol):
    #    for k in range(ip[j], ip[j+1]-1):
    #        if ind[k] >= ind[k+1]:
    #            raise ValueError, 'Rows must be ordered in each column.'

    # Set mxtype.
    mxtype0 = 'r'
    if pattern_only:
        mxtype0 = 'p'
    if symmetric:
        mxtype1 = 's'
    if skew:
        mxtype1 = 'z'
    if rectangular:
        mxtype1 = 'r'

    mxtype = mxtype0 + mxtype1 + 'a'

    # Set format and number card images for pointer array.
    (ptrfmt, ptrn) = get_int_fmt(ne + 1)
    ptrcrd = ncol / ptrn + 1

    # Set format and number card images for index array.
    (indfmt, indn) = get_int_fmt(nrow)
    indcrd = (ne - 1) / indn + 1

    # Set number of card images for numerical entries.
    if pattern_only:
        valcrd = 0
        valfmi = ' '
    else:
        (valfmi, valfmo, valn) = get_real_fmt(precision)
        valcrd = (ne - 1) / valn + 1

    totcrd = ptrcrd + indcrd + valcrd
    neltvl = 0

    fp = open(fname, 'w')

    lt = len(title)
    if lt < 72:
        title = title + (72 - lt) * ' '
    lk = len(key)
    if lk < 8:
        key = key + (8 - lk) * ' '

    # Write header.
    fortran_write_line([title, key], fp, 'A72,A8')
    fortran_write_line([totcrd, ptrcrd, indcrd, valcrd], fp, 'I14,3(1X,I13)')
    fortran_write_line([mxtype, nrow, ncol, ne, neltvl], fp, 'A3,11X,4(1X,I13)')
    fortran_write_line([ptrfmt, indfmt, valfmi], fp, '2A16,A20')

    # Write pointer and index arrays. Ajust for 1-based indexing.
    # print 'Writing pointer array...'
    fortran_write_array(ip + 1, ptrn, fp, ptrfmt)
    # print 'Writing index array...'
    fortran_write_array(ind + 1, indn, fp, indfmt)

    # Write matrix entries.
    neltvl = ne
    if not pattern_only:
        # print 'Writing matrix entries...'
        fortran_write_array(val, valn, fp, valfmo)

    fp.close()
    return


def write_rb_from_rb(fname, matrix):
    """Write a matrix in RB format to file."""
    (ip, ind, val) = matrix.data()
    write_rb(fname, matrix.nrow, matrix.ncol, ip, ind, val,
             symmetric=matrix.issym)
    return


def write_rb_from_coord(fname, nrow, ncol, irow, jcol, val=None, **kwargs):
    """Write a matrix in coord format to file in RB format."""
    (ind, ip, values) = coord2csc(ncol, irow, jcol, val)
    write_rb(fname, nrow, ncol, ip, ind, val, **kwargs)
    return


def write_aux(fname, nrow, nvec, precision=17, title='Generic', key='Generic',
              caseid='Generic', dattyp='rhs', positn='r', orgniz='d', nauxd=None,
              ip=None, ind=None, val=None):
    """Write supplementary data to file in Rutherford-Boeing format.

    Only real data is supported for now.
    """

    data_types = ['ord', 'rhs', 'sln', 'est', 'evl', 'svl', 'evc', 'svc',
                  'sbv', 'sbm', 'sbp', 'ipt', 'icv', 'lvl', 'geo', 'avl']
    organizations = ['s', 'd', 'e']
    positions = ['r', 'l', 's']

    if dattyp not in data_types:
        raise ValueError, 'Unknown data type: %s' % dattyp
    if positn not in positions:
        raise ValueError, 'Unknown position: %s' % positn
    if orgniz not in organizations:
        raise ValueError, 'Unknown organization: %s' % orgniz

    if dattyp in ['evl', 'svl', 'lvl', 'sbp']:
        nvec = 1
    if dattyp in ['evl', 'svl', 'lvl', 'sbv', 'sbm', 'sbp', 'avl']:
        positn = ' '
    if dattyp != 'rhs':
        orgniz = ' '

    numerf = 'r'
    if dattyp == 'ord':
        numerf = 'i'
    if dattyp in ['ipt', 'icv']:
        numerf = 'p'

    if orgniz != 'e':
        nauxd = 0
        if orgniz == 's' or dattyp in ['icv', 'ipt']:
            if ip is None:
                raise ValueError('Need pointer array for data type %s', dattyp)
            nauxd = ip(nvec) - 1
        if orgniz == 'd':
            nauxd = nrow * nvec

    # Set data formats.
    auxfm1 = auxfm2 = auxfm3 = ' '
    fm1 = fm3 = ' '

    if dattyp in ['ipt', 'icv']:
        (auxfm1, n1) = get_int_fmt(nauxd + 1)
        (auxfm2, n2) = get_int_fmt(nrow)
    elif dattyp == 'ord':
        (auxfm1, n1) = get_int_fmt(nrow)
    else:
        if precision < 2 or precision > 17:
            precision = 17
        if dattyp == 'rhs' and orgniz == 's':
            (auxfm1, n1) = get_int_fmt(nauxd + 1)
            (auxfm2, n2) = get_int_fmt(nrow)
            (auxfm3, fm3, n3) = get_real_fmt(precision)
        else:
            (auxfm1, fm1, n1) = get_real_fmt(precision)

    fp = open(fname, 'w')

    lt = len(title)
    if lt < 72:
        title = title + (72 - lt) * ' '
    lk = len(key)
    if lk < 8:
        key = key + (8 - lk) * ' '

    # Write header.
    fortran_write_line([title, key], fp, 'A72,A8')
    fortran_write_line([dattyp, positn, orgniz, caseid, numerf, nrow, nvec,
                        nauxd], fp, 'A3,2A1,1X,A8,1X,A1,3(1X,I13)')
    fortran_write_line([auxfm1, auxfm2, auxfm3], fp, '3A20')

    # Write pointer and index arrays. Ajust for 1-based indexing.
    if (dattyp == 'rhs' and orgniz == 's') or dattyp in ['ipt', 'icv']:
        # print 'Writing pointer array...'
        fortran_write_array(ip + 1, n1, fp, auxfm1)
        # print 'Writing index array...'
        fortran_write_array(ind + 1, n2, fp, auxfm2)

    # Write entries.
    # print 'Writing entries...'
    if dattyp == 'rhs' and orgniz == 's':
        fortran_write_array(val, n3, fp, fm3)
    else:
        fortran_write_array(val, n1, fp, fm1)

    fp.close()
    return


def write_aux_from_rb(fname, rbdata):
    """Write supplementary data in RB format to file."""
    (ip, ind, val) = rbdata.data()
    write_aux(fname, rbdata.nrow, ip.shape[0], dattyp=rbdata.dattyp,
              title=rbdata.title, key=rbdata.key, caseid=rbdata.caseid,
              positn=rbdata.positn, orgniz=rbdata.orgniz, nauxd=rbdata.nauxd,
              ip=ip, ind=ind, val=val)


def write_aux_from_numpy(fname, array, **kwargs):
    """Write a numpy array to file in RB format."""
    if len(array.shape) == 1:
        nvec = 1
    else:
        nvec = array.shape[1]
    write_aux(fname, array.shape[0], nvec, val=array, **kwargs)


if __name__ == '__main__':

    # Demo the HarwellBoeingMatrix and RutherfordBoeingData classes
    # In case of Rutherford-Boeing supplementary data, some of the following
    # may not make sense.

    import sys
    fname = sys.argv[1]
    plot = False

    np.set_printoptions(precision=8,
                        threshold=10,
                        edgeitems=3,
                        linewidth=80,
                        suppress=False)

    # M = HarwellBoeingMatrix(fname, pattern_only=False, read_rhs=True)
    # Comment this out for Rutherford-Boeing data
    # if M.read_rhs:
    #    for i in range(M.nrhs):
    #        print M.rhs[:,i]

    M = RutherfordBoeingData(fname, pattern_only=False)
    print 'Data of order (%-d,%-d) with %-d nonzeros' % (M.nrow, M.ncol, M.nnzero)

    # Plot sparsity pattern
    if plot:
        try:
            import pylab
        except:
            sys.stderr.write('Pylab is required for the demo\n')
            sys.exit(1)

        (val, row, col) = M.find()
        fig = pylab.figure()
        ax = fig.gca()
        ax.plot(col, row, 'ks', markersize=1, linestyle='None')
        if M.issym:
            ax.plot(row, col, 'ks', markersize=1, linestyle='None')
        ax.set_xlim(xmin=-1, xmax=M.ncol)
        ax.set_ylim(ymin=M.nrow, ymax=-1)
        if M.nrow == M.ncol:
            ax.set_aspect('equal')
        pylab.title(M.title, fontsize='small')
        pylab.show()

    # Write data back to file
    # (ip, ind, val) = M.data()
    # print val
    # write_rb('newmat.rb', M.nrow, M.ncol, ip, ind, val, symmetric=M.issym)
    x = np.ones(M.ncol)
    # y = M*x
    # write_aux_from_numpy('rhs.rb', y)
    write_aux_from_numpy('sol.rb', x)
