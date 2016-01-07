HSL.py
======

HSL.py is a set of Cython/Python interfaces to some of the [Harwell Subroutine Library](http://www.hsl.rl.ac.uk/): a collection of state-of-the-art packages for large-scale scientific computation.
These packages are written mostly in Fortran and often provide C interfaces but no Python interfaces.

HSL.py provides interfaces to

- ordering methods:
    - [mc21](http://www.hsl.rl.ac.uk/catalogue/mc21.html): permute a sparse matrix to put entries on the diagonal (single and double precision);
    - [mc60](http://www.hsl.rl.ac.uk/catalogue/mc60.html): reduce the profile and wavefront of a sparse symmetric (single and double precision);
- scaling methods:
    - [mc29](http://www.hsl.rl.ac.uk/catalogue/mc29.html): calculate scaling factors of a sparse (un)symmetric matrix (single and double precision);
- linear solvers:
    - [ma27](http://www.hsl.rl.ac.uk/download/MA27/1.0.0/a/): solve sparse symmetric system, not necessarily positive definite (single and double precision);
    - [ma57](http://www.hsl.rl.ac.uk/catalogue/ma57.html): solve a sparse symmetric system using a multifrontal method (single and double precision).


## Dependencies
In order to build previous interfaces, you **need** to provide source code from the [Harwell Subroutine Library](http://www.hsl.rl.ac.uk/).
All required packages are available free of charge to academics.
Just follow hyperlinks in upper section and fill the licence agreement on their website and you are done!

HSL.py also depends on

- NumPy;
- CySparse;

If you intend to generate the documentation:

- Sphinx;
- sphinx_bootstrap_theme;

To run the tests:

- nose;


## Installation


1. Clone repository

		git clone git@github.com:optimizers/HSL.py.git
	
2. Install Python dependencies

		pip install numpy
		pip install cysparse (one day ;))

3. Copy `site.template.cfg` to `site.cfg` and adjust it to your needs.
4. Install HSL.py

		python setup.py install. 

## Compilation of cython files

    cython -I ~/work/VirtualEnvs/nlpy_new/programs/cysparse/ _cyma57.pyx


## TODO

- [ ] make it work with CySparse
- [ ] create documentation
- [ ] add tests
- [ ] make it work for single precision (cygenja?)
