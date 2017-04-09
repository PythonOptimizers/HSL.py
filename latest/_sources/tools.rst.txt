..  hsl_tools:

Tools
=====


Conversion
~~~~~~~~~~

.. _conversion-section:

.. automodule:: hsl.tools.conversion

.. autofunction:: coord2csc

.. autofunction:: csc2coord


Matrix readers
~~~~~~~~~~~~~~

.. _readers-section:

.. automodule:: hsl.tools.hrb

.. autoclass:: HarwellBoeingMatrix
   :show-inheritance:
   :members:
   :inherited-members:
   :undoc-members:

.. autoclass:: RutherfordBoeingData
  :show-inheritance:
  :members:
  :inherited-members:
  :undoc-members:


.. automodule:: hsl.tools.mtx

.. autoclass:: MatrixMarketMatrix
  :show-inheritance:
  :members:
  :inherited-members:
  :undoc-members:


Sparsity pattern
~~~~~~~~~~~~~~~~

.. automodule:: hsl.tools.spy

.. autofunction:: spy

.. autofunction:: fast_spy

Example
~~~~~~~

.. literalinclude:: ../../examples/demo_hb_mc21.py
 :linenos:

.. figure:: mc21.*

The sparsity pattern of the orginal matrix is shown on the left plot.
The right plot show sthe same matrix after usage of the `nonzerodiag` function which
attempts to find a row permutation so the row-permuted matrix has a nonzero diagonal, if this is possible. 
