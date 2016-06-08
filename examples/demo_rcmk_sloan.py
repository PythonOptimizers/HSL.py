from hsl.ordering.mc60 import sloan, rcmk
from cysparse.sparse.ll_mat import *
import cysparse.types.cysparse_types as types

from hsl.tools.spy import fast_spy
import numpy as np
import matplotlib.pyplot as plt


A = LLSparseMatrix(mm_filename='bcsstk01.mtx',
                   itype=types.INT32_T, dtype=types.FLOAT64_T)
m, n = A.shape
irow, jcol, val = A.find()

A_csc = A.to_csc()
colptr, rowind, values = A_csc.get_numpy_arrays()

perm1, rinfo1 = rcmk(n, rowind, colptr)   # Reverse Cuthill-McKee
perm2, rinfo2 = sloan(n, rowind, colptr)  # Sloan's method

left = plt.subplot(131)
fast_spy(n, n, irow, jcol, sym=True,
         ax=left.get_axes(), title='Original')

# Apply permutation 1 and plot reordered matrix
middle = plt.subplot(132)
fast_spy(n, n, perm1[irow], perm1[jcol], sym=True,
         ax=middle.get_axes(), title='Rev. Cuthill-McKee (semibandwidth=%d)' % rinfo1[2])

# Apply permutation 2 and plot reordered matrix
right = plt.subplot(133)
fast_spy(n, n, perm2[irow], perm2[jcol], sym=True,
         ax=right.get_axes(), title='Sloan (semibandwidth=%d)' % rinfo2[2])

plt.savefig('mc60_rcmk_sloan.png', bbox_inches='tight')
# plt.show()
