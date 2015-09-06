#!/usr/bin/env python

import pysparse
import numpy
import os
import ConfigParser
from numpy.distutils.misc_util import Configuration
from numpy.distutils.system_info import get_info, NotFoundError
from numpy.distutils.core import setup

# For debugging f2py extensions:
f2py_options = []
#f2py_options.append('--debug-capi')

top_path = ''
parent_package=''

pysparse_inc = pysparse.get_include()
cysparse_inc = "/Users/syarra/work/VirtualEnvs/sparseldlt/programs/cysparse/"

# Read relevant configuration options.
hsl_config = ConfigParser.SafeConfigParser()
hsl_config.read(os.path.join(top_path, 'site.cfg'))
hsl_dir = hsl_config.get('HSL', 'hsl_dir')
metis_dir = hsl_config.get('METIS', 'metis_dir')
metis_lib = hsl_config.get('METIS', 'metis_lib')

config = Configuration('hsl', parent_package, top_path)
config.set_options(ignore_setup_xxx_py=True,
                   assume_default_configuration=True,
                   delegate_options_to_subpackages=True,
                   quiet=True)


config.add_include_dirs([numpy.get_include(), pysparse.get_include()])
config.add_include_dirs('include')
 
# Get info from site.cfg
blas_info = get_info('blas_opt',0)
if not blas_info:
    print 'No blas info found'

lapack_info = get_info('lapack_opt',0)
if not lapack_info:
    print 'No lapack info found'

# Relevant files for building MA27 extension.
ma27_src = ['fd05ad.f', 'ma27ad.f']
libma27_src = ['ma27fact.f']
pyma27_src = ['ma27_lib.c','hsl_alloc.c','_pyma27.c']

# Build PyMA27
ma27_sources  = [os.path.join(hsl_dir,name) for name in ma27_src]
ma27_sources += [os.path.join('hsl','solvers','src',name) for name in libma27_src]
pyma27_sources = [os.path.join('hsl','solvers','src',name) for name in pyma27_src]

config.add_library(
        name='hsl_ma27',
        sources=ma27_sources,
        include_dirs=[hsl_dir, os.path.join('hsl','solvers','src')],
        extra_info=blas_info,
        )


config.add_extension(
    name='solvers._pyma27',
    sources=pyma27_sources,
    depends=[],
    libraries=['hsl_ma27'],
    include_dirs=['include', os.path.join('hsl','solvers','src')],
    extra_info=blas_info,
    )

# Build PyMA57
ma57_src = ['ddeps.f', 'ma57d.f']
ma57_sources = [os.path.join(hsl_dir,'ma57d',name) for name in ma57_src]

config.add_library(
        name='hsl_ma57',
        sources=ma57_sources,
        libraries=[metis_lib],
        library_dirs=[metis_dir],
        include_dirs=[hsl_dir, os.path.join('hsl','solvers','src')],
        extra_info=blas_info,
        )

pyma57_src = ['ma57_lib.c','hsl_alloc.c','_pyma57.c']
pyma57_sources = [os.path.join('hsl','solvers','src',name) for name in pyma57_src]

config.add_extension(
    name='solvers._pyma57',
    sources=pyma57_sources,
    libraries=[metis_lib,'hsl_ma57'],
    library_dirs=[metis_dir],
    include_dirs=['include',os.path.join('hsl','solvers','src')],
    extra_info=blas_info,
    )

cyma57_src = ['ma57_lib.c','hsl_alloc.c','_cyma57.c']
cyma57_sources = [os.path.join('hsl','solvers','src',name) for name in cyma57_src]

config.add_extension(
    name='solvers._cyma57',
    sources=cyma57_sources,
    libraries=[metis_lib,'hsl_ma57'],
    library_dirs=[metis_dir],
    include_dirs=[cysparse_inc,'include',os.path.join('hsl','solvers','src')],
    extra_info=blas_info,
    )


mc29_sources = [os.path.join(hsl_dir,'mc29d','mc29d.f'),
                os.path.join('hsl', 'scaling', 'src','mc29.pyf')]

config.add_extension(
        name='scaling._mc29',
        sources=mc29_sources,
        include_dirs=[os.path.join('hsl','scaling','src')],
        extra_link_args=[])


mc21_sources = [os.path.join(hsl_dir,'mc21d','mc21d.f'),
                os.path.join('hsl', 'ordering', 'src','mc21.pyf')]

config.add_extension(
        name='ordering._mc21',
        sources=mc21_sources,
        include_dirs=[os.path.join('hsl','ordering','src')],
        extra_link_args=[])


mc60_sources = [os.path.join(hsl_dir,'mc60d','mc60d.f'),
                os.path.join('hsl', 'ordering', 'src','mc60.pyf')]

config.add_extension(
        name='ordering._mc60',
        sources=mc60_sources,
        include_dirs=[os.path.join('hsl','ordering','src')],
        extra_link_args=[])


config.make_config_py()

setup(**config.todict())
