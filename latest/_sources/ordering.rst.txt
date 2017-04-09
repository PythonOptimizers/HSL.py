.. Description of ordering module
.. _ordering-page:

===================================
Ordering method for sparse matrices
===================================



The :mod:`mc21` Module
======================

.. _mc21-section:

.. automodule:: hsl.ordering.mc21

.. autofunction:: nonzerodiag


The :mod:`mc60` Module
========================

.. automodule:: hsl.ordering.mc60

Sloan's algorithm
-----------------

.. autofunction:: sloan

Reverse Cuthill-McKee algorithm 
-------------------------------

.. autofunction:: rcmk

Example
-------

.. literalinclude:: ../../examples/demo_mc60.py
   :linenos:

.. code-block:: none

   The number of supervariables is  4
   The variable permutation is  [3 5 4 1 2]
   The profile is  10.0
   The maximum wavefront is  3.0
   The semibandwidth is  3.0
   The root-mean-square wavefront is  2.09761769634

Using a matrix market matrix through :program:`CySparse`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. literalinclude:: ../../examples/demo_rcmk_sloan.py
   :linenos:

.. figure:: mc60_rcmk_sloan.*

   The sparsity pattern of the orginal matrix is shown on the left plot.
   The middle and right plots show the same matrix after a symmetric permutation of the rows and columns
   aiming to reduce the bandwidth, profile and/or wavefront. This is done respectively via the
   reverse Cuthill-McKee method and the algorithm of Sloan.


