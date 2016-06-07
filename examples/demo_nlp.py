
try:
    from nlp.model.amplmodel import AmplModel
except ImportError:
    msg='NLP.py is required to run this demo.'
    msg+=' See https://github.com/PythonOptimizers/NLP.py'
    raise RuntimeError, msg

from pyorder.tools import coord2csc
from hsl.ordering.mc60 import sloan, rcmk
from pyorder.tools.spy import FastSpy
import numpy as np
import matplotlib.pyplot as plt
import os

this_path = os.path.dirname(os.path.realpath(__file__))

model = AmplModel(os.path.join(this_path, 'truss18bars.nl'))
x = np.random.random(model.n)
y = np.random.random(model.m)
(val,irow,jcol) = model.hess(x,y)
(rowind, colptr, values) = coord2csc(model.n, irow, jcol, val)  # Convert to CSC

perm1, rinfo1 = rcmk(model.n, rowind, colptr)   # Reverse Cuthill-McKee
perm2, rinfo2 = sloan(model.n, rowind, colptr)  # Sloan's method

left = plt.subplot(131)
FastSpy(model.n, model.n, irow, jcol, sym=True,
        ax=left.get_axes(), title='Original')

# Apply permutation 1 and plot reordered matrix
middle = plt.subplot(132)
FastSpy(model.n, model.n, perm1[irow], perm1[jcol], sym=True,
        ax=middle.get_axes(), title='Rev. Cuthill-McKee (semibandwidth=%d)' % rinfo1[2])

# Apply permutation 2 and plot reordered matrix
right = plt.subplot(133)
FastSpy(model.n, model.n, perm2[irow], perm2[jcol], sym=True,
        ax=right.get_axes(), title='Sloan (semibandwidth=%d)' % rinfo2[2])

#plt.savefig('mpvc.pdf',bbox_inches='tight')
plt.show()
