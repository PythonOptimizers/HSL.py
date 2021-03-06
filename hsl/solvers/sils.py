"""
SILS: An abstract framework for the factorization of symmetric indefinite
matrices. The factorizations currently implemented are those of MA27 and MA57
from the Harwell Subroutine Library (http://hsl.rl.ac.uk).
"""

import numpy


class Sils(object):
    """Abstract class for the solution of symmetric indefinite linear systems.

    The methods of this class must be overridden.
    """

    def __init__(self, A, **kwargs):
        """Instantiate a :class:`Sils` object.
        :parameter:
            :A: A ll_mat format matrix that should be symmetric.

        :keywords:
            :sqd:  Flag indicating symmetric quasi-definite matrix
                   (default: False)
        """

        try:
            symmetric = A.issym
        except:
            symmetric = A.is_symmetric

        if not symmetric:
            raise ValueError('Input matrix must be symmetric')
        self.n = A.shape[0]
        self.sqd = 'sqd' in kwargs and kwargs['sqd']

        # Solution and residual vectors
        self.x = numpy.zeros(self.n)
        self.residual = numpy.zeros(self.n)

        self.context = None

    def solve(self, b, get_resid=True):
        """Must be subclassed."""
        raise NotImplementedError

    def refine(self, b, nitref=3):
        """Must be subclassed."""
        raise NotImplementedError

    def fetch_perm(self):
        """Must be subclassed."""
        raise NotImplementedError
