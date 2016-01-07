"Exemple from MC29 spec sheet: http://www.hsl.rl.ac.uk/specs/mc29.pdf"

from hsl.scaling._mc29 import mc29ad
import numpy as np

irow = np.array([3,0,3,1,2,2], dtype=np.int32)
jcol = np.array([2,0,1,1,0,2], dtype=np.int32)
values = np.array([16000, 100, 14000, 6, 900, 110000], dtype=np.float64)
print 'orignal values:'
print values

# Obtain row and column scaling
row_scale, col_scale, ifail = mc29ad(4, 3, values, irow+1, jcol+1)

if ifail==-1:
    raise ValueError("m < 1 or n < 1")
elif ifail==-2:
    raise ValueError("number of non zero elemnts < 1")

# row_scale and col_scale contain in fact the logarithms of the
# scaling factors.
row_scale = np.exp(row_scale)
col_scale = np.exp(col_scale)

print '\nrow scaling factors:'
print row_scale

print '\ncolumn scaling factors:'
print col_scale

# Apply row and column scaling to constraint matrix A.
values *= row_scale[irow]
values *= col_scale[jcol]

print '\nscaled values'
print values
