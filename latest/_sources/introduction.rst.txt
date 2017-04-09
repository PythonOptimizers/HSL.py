.. introduction_to_hsl:

Introduction
============

:program:`HSL.py` is a set of Cython/Python interfaces to some of the `Harwell Subroutine Library <http://www.hsl.rl.ac.uk/>`_: a collection of state-of-the-art packages for large-scale scientific computation.
These packages are written mostly in Fortran and often provide C interfaces but no Python interfaces.

:program:`HSL.py` provides interfaces to

- ordering methods:
    - `mc21 <http://www.hsl.rl.ac.uk/catalogue/mc21.html>`_: permute a sparse matrix to put entries on the diagonal (single and double precision);
    - `mc60 <http://www.hsl.rl.ac.uk/catalogue/mc60.html>`_: reduce the profile and wavefront of a sparse symmetric (single and double precision);
- scaling methods:
    - `mc29 <http://www.hsl.rl.ac.uk/catalogue/mc29.html>`_: calculate scaling factors of a sparse (un)symmetric matrix (single and double precision);
- linear solvers:
    - `ma27 <http://www.hsl.rl.ac.uk/download/MA27/1.0.0/a/>`_: solve sparse symmetric system, not necessarily positive definite (single and double precision);
    - `ma57 <http://www.hsl.rl.ac.uk/catalogue/ma57.html>`_: solve a sparse symmetric system using a multifrontal method (single and double precision).


Dependencies
~~~~~~~~~~~~

In order to build previous interfaces, you **need** to provide source code from the `Harwell Subroutine Library <http://www.hsl.rl.ac.uk/>`_.
All required packages are available free of charge to academics.
Just follow hyperlinks in upper section and fill the licence agreement on their website and you are done!


License
~~~~~~~

The :program:`HSL.py` library is released under the `GNU Lesser General Public License <http://www.gnu.org/licenses/lgpl-3.0.en.html>`_ (LGPL), version 3.
