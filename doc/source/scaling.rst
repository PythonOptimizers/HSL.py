.. Description of scaling module
.. _scaling-page:

===================================
Scaling method for sparse matrices
===================================



The :mod:`mc29` Module
======================

.. _mc29-section:

.. automodule:: hsl.scaling.mc29

.. autofunction:: MC29AD_scale

.. autofunction:: unscale

Example
=======

.. literalinclude:: ../../examples/demo_mc29.py
   :linenos:

Output

.. code-block:: bash

   orignal values:
    i  j    val
    3  2 1.60000e+04
    0  0 1.00000e+02
    3  1 1.40000e+04
    1  1 6.00000e+00
    2  0 9.00000e+02
    2  2 1.10000e+05

   row scaling factors:
   [  2.17526613e+00   5.55712076e+02   7.35847733e-02   3.90868730e-01]

   column scaling factors:
   [ 0.0083316   0.00023411  0.00014055]

   scaled values:
    i  j    val
    3  2 8.78992e-01
    0  0 1.81235e+00
    3  1 1.28109e+00
    1  1 7.80587e-01
    2  0 5.51771e-01
    2  2 1.13767e+00

   unscaled values:
    i  j    val
    3  2 1.60000e+04
    0  0 1.00000e+02
    3  1 1.40000e+04
    1  1 6.00000e+00
    2  0 9.00000e+02
    2  2 1.10000e+05
