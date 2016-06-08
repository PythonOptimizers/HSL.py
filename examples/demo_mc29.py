"""Exemple from MC29 spec sheet: http://www.hsl.rl.ac.uk/specs/mc29.pdf

IN PLACE scaling.
"""

from hsl.scaling.mc29 import MC29AD_scale, unscale
import numpy as np

irow = np.array([3, 0, 3, 1, 2, 2], dtype=np.int32)
jcol = np.array([2, 0, 1, 1, 0, 2], dtype=np.int32)
values = np.array([16000, 100, 14000, 6, 900, 110000], dtype=np.float64)
print 'orignal values:'
print '%2s % 2s %6s' % ('i', 'j', 'val')
for i in range(0, len(values)):
    print '%2d % 2d %6.5e' % (irow[i], jcol[i], values[i])

# Obtain row and column scaling
row_scale, col_scale = MC29AD_scale(4, 3, irow, jcol, values)

print '\nrow scaling factors:'
print row_scale

print '\ncolumn scaling factors:'
print col_scale

print '\nscaled values:'
print '%2s % 2s %6s' % ('i', 'j', 'val')
for i in range(0, len(values)):
    print '%2d % 2d %6.5e' % (irow[i], jcol[i], values[i])


unscale(4, 3, row_scale, col_scale, irow, jcol, values)
print '\nunscaled values:'
print '%2s % 2s %6s' % ('i', 'j', 'val')
for i in range(0, len(values)):
    print '%2d % 2d %6.5e' % (irow[i], jcol[i], values[i])
