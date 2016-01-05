..  hsl_intallation:

===================================
Installation
===================================

:program:`HSL.py` uses external packages that are not included in the :program:`HSL.py`
source code because they are released under different licenses than the one used for
:program:`HSL.py`. Hence we cannot distribute their code and you have to obtain them yourself.

HSL routines
============

HSL website is divided into two parts:

1. **Archive**, which contains outdated codes that are freely available for personal commercial or
   non-commercial usage. It includes, amongst other, MA27 and MC19.

2. **Academic access**, which contains more modern codes that are freely available for academic use only.
   It includes, amongst other, MC21, MC60, MA57, MA87, and MA97.
   
To obtain the HSL code, go to the `HSL website <http://www.hsl.rl.ac.uk/>`_ and download desired source code.

You do **not** need to compile them by yourself. We will do it for you.

Note: If you are an academic or a student, we recommend you download and use MA57 instead of MA27, because 
it can be considerably faster than MA27 on some problems.

METIS (optional)
================

The linear solvers MA57, MA87 and MA97 can make use of the matrix ordering algorithms implemented in 
`METIS <http://glaros.dtc.umn.edu/gkhome/metis/metis/overview>`_.
If you are using one of these linear solvers, you should obtain the :program:`METIS` source code and compile it.

If you are under OS X, a `Homebrew <http://brew.sh>`_ formula is available. Follow the instructions to install Homebrew.
Then, :program:`metis` and its dependencies can be installed automatically in `/usr/local` by typing

.. code-block:: bash

    brew tap homebrew/science
    brew install metis



:program:`Python` interfaces
============================

:program:`HSL.py` installation is done in few simple steps:

1. Clone the repository:

  ..  code-block:: bash

      git clone https://github.com/PythonOptimizers/cysparse.git


2. Install the :program:`Python` dependencies:

- :program:`NumPy`
- :program:`CySparse`

  Python installer :program:`pip` is recommended for that

  ..  code-block:: bash

      pip install numpy
      pip install CySparse


3. Copy :file:`site.template.cfg` to :file:`site.cfg` and adjust it to reflect your own environment

4. Compile and install the library:

  The preferred way to install the library is to install it in its own `virtualenv`.

  To compile and install the library, just type

      ..  code-block:: bash

          python setup.py install



Further dependencies
====================

Documentation
-------------

To generate the documentation you will need other Python dependencies:

- :program:`Sphinx`
- :program:`sphinx-bootstrap-theme`

which can be easily installed using :program:`pip`


Testing
-------
Testing is done using :program:`nose`, so it needs to be installed before running them.


Note that a complete list of dependencies is provided in the :file:`requirements.txt` file. You can easily install all of them with:

..  code-block:: bash

    pip install -r requirements.txt

