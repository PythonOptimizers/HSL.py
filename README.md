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

Some routines such as MA57 optionnaly uses the [METIS](http://glaros.dtc.umn.edu/gkhome/views/metis) library.
If you are under OS X, a [Homebrew](http://brew.sh) formula is available. 
Follow the instructions to install Homebrew. Then, METIS and its dependencies can be installed automatically in `/usr/local` by typing

            brew tap homebrew/science

            brew install metis4

Only METIS version 4 is supported by MA57.


HSL.py also depends on

- NumPy;


And optionaly on
- CySparse;

If you intend to generate the documentation:

- Sphinx;
- sphinx_bootstrap_theme;

To run the tests:

- nose;


## Installation

### branch `master`

1. Clone repository

		git clone git@github.com:optimizers/HSL.py.git
	
2. Install Python dependencies

		pip install numpy
		pip install cysparse (one day ;))  (optional)

3. Copy `site.template.cfg` to `site.cfg` and adjust it to your needs.

4. Install HSL.py

		python setup.py install. 


### branch `develop`

1. Clone repository

		git clone git@github.com:optimizers/HSL.py.git
	
2. Install Python dependencies

		pip install numpy
        pip install cygenja
		pip install cysparse (one day ;))  (optional)

3. Copy `site.template.cfg` to `site.cfg` and adjust it to your needs.

4. Generate cython files:
        
        python generate_code.py

4. Install HSL.py

		python setup.py install. 



## Note
weird behaviour of Cython, cannot cythonize some .pyx files using setup.py but works when invoking cython from command line ...
So I modified setup.py to create c file using command line "cython"

    cython -I ~/work/VirtualEnvs/nlpy_new/programs/cysparse/_cyma57.pyx

## TODO

- [ ] remove pysparse from cyma27
- [x] remove pysparse from cyma57
- [x] make it work with CySparse
- [x] create documentation
- [ ] update documentation
- [ ] add more tests
- [ ] make it work for single precision (cygenja?)
