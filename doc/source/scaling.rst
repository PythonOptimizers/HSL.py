.. Description of scaling module
.. _scaling-page:

===================================
Scaling method for sparse matrices
===================================



The :mod:`mc29` Module
======================

.. _mc29-section:

Example
-------

.. literalinclude:: ../../examples/demo_mc29.py
   :linenos:

Output

.. code-block:: python

   orignal values:
   [  1.60000000e+04   1.00000000e+02   1.40000000e+04   6.00000000e+00
   9.00000000e+02   1.10000000e+05]

   row scaling factors:
   [  2.17526613e+00   5.55712076e+02   7.35847733e-02   3.90868730e-01]

   column scaling factors:
   [ 0.0083316   0.00023411  0.00014055]

   scaled values
   [ 0.87899243  1.81234539  1.28108793  0.78058654  0.55177121  1.13766623]
