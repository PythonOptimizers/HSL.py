"""Illustrate usage of Harwell-Boeing or Rutherford-Boeing readers and mc21.

Supply a file name as input argument on the command line and uncomment below as
appropriate.
"""

import sys
from hsl.ordering.mc21 import nonzerodiag
from hsl.tools.hrb import HarwellBoeingMatrix, RutherfordBoeingData

if len(sys.argv) < 2:
    sys.stderr.write('Supply input matrix as argument\n')
    sys.exit(1)

fname = sys.argv[1]
# M = HarwellBoeingMatrix(fname, patternOnly=True, readRhs=False)
M = RutherfordBoeingData(fname, patternOnly=True, readRhs=False)

if M.nrow != M.ncol:
    sys.stderr.write('Input matrix must be square\n')
    sys.exit(1)

perm, nzdiag = nonzerodiag(M.nrow, M.ind, M.ip)
print 'Number of nonzeros on diagonal after reordering: ', nzdiag

try:
    from hsl.tools.spy import fast_spy
    import pylab
    (_, irow, jcol) = M.find()
    left = pylab.subplot(121)
    fast_spy(M.nrow, M.ncol, irow, jcol, sym=M.issym, ax=left.get_axes())

    right = pylab.subplot(122)
    fast_spy(M.nrow, M.ncol, perm[irow], jcol, sym=M.issym, ax=right.get_axes())
    pylab.show()
    # pylab.savefig('mc21.pdf', bbox_inches='tight')

except:
    pass
