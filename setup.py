#!/usr/bin/env python

# The file setup.py is automatically generated
# Generate it with
# python generate_code

import pysparse
from distutils.core import setup
from setuptools import find_packages
from distutils.extension import Extension
from Cython.Distutils import build_ext
from numpy.distutils.misc_util import Configuration
from numpy.distutils.system_info import get_info
from numpy.distutils.core import setup

from Cython.Build import cythonize

import numpy as np

import ConfigParser
import os
import copy

from codecs import open
from os import path


from subprocess import call

# HELPERS
#--------
def prepare_Cython_extensions_as_C_extensions(extensions):
    """
    Modify the list of sources to transform `Cython` extensions into `C` extensions.
    Args:
        extensions: A list of (`Cython`) `distutils` extensions.
    Warning:
        The extensions are changed in place. This function is not compatible with `C++` code.
    Note:
        Only `Cython` source files are modified into their `C` equivalent source files. Other file types are unchanged.
    """
    for extension in extensions:
        c_sources = list()
        for source_path in extension.sources:
            path, source = os.path.split(source_path)
            filename, ext = os.path.splitext(source)

            if ext == '.pyx':
                c_sources.append(os.path.join(path, filename + '.c'))
            elif ext in ['.pxd', '.pxi']:
                pass
            else:
                # copy source as is
                c_sources.append(source_path)

        # modify extension in place
        extension.sources = c_sources
           
def files_exist(file_list):
    for fname in file_list:
        if os.path.isfile(fname) == False:
            return False
    return True

f2py_options = []
           
hsl_config = ConfigParser.SafeConfigParser()
hsl_config.read('site.cfg')

version = {}
with open(os.path.join('hsl', 'version.py')) as fp:
      exec(fp.read(), version)
# later on we use: version['version']

numpy_include = np.get_include()
pysparse_inc = pysparse.get_include()

# Use Cython?
use_cython = hsl_config.getboolean('CODE_GENERATION', 'use_cython')
if use_cython:
    try:
        from Cython.Distutils import build_ext
        from Cython.Build import cythonize
    except ImportError:
        raise ImportError("Check '%s': Cython is not properly installed." % hsl_config_file)

# DEFAULT
default_include_dir = hsl_config.get('DEFAULT', 'include_dirs').split(os.pathsep)
default_library_dir = hsl_config.get('DEFAULT', 'library_dirs').split(os.pathsep)

# Debug mode
use_debug_symbols = hsl_config.getboolean('CODE_GENERATION', 'use_debug_symbols')

# find user defined directories
hsl_rootdir = hsl_config.get('HSL', 'hsl_rootdir')
if hsl_rootdir == '':
    raise ValueError("Please provide HSL source directory!")

metis_dir = hsl_config.get('METIS', 'metis_dir')
metis_lib = hsl_config.get('METIS', 'metis_lib')

# OPTIONAL
build_cysparse_ext = False           
if hsl_config.has_section('CYSPARSE'):
    build_cysparse_ext = True
    cysparse_rootdir = hsl_config.get('CYSPARSE', 'cysparse_rootdir').split(os.pathsep)
    if cysparse_rootdir == '':
        raise ValueError("You must specify where CySparse source code is" +
                         "located. Use `cysparse_rootdir` to specify its path.")

config = Configuration('hsl', '', '')
config.set_options(ignore_setup_xxx_py=True,
                   assume_default_configuration=True,
                   delegate_options_to_subpackages=True,
                   quiet=True)

# Set config.version
config.get_version(os.path.join('hsl', 'version.py'))


config.add_include_dirs([np.get_include(), pysparse.get_include()])
config.add_include_dirs('include')

# Get info from site.cfg
blas_info = get_info('blas_opt', 0)
if not blas_info:
    print 'No blas info found'

lapack_info = get_info('lapack_opt', 0)
if not lapack_info:
    print 'No lapack info found'

           
########################################################################################################################
# EXTENSIONS
########################################################################################################################
include_dirs = [numpy_include, 'include', '.']

## Extensions using Fortran codes 

# Relevant files for building MA27 extension.
ma27_src = ['fd05ad.f', 'ma27ad.f']
libma27_src = ['ma27fact.f']
pyma27_src = ['ma27_lib.c', 'hsl_alloc.c', '_pyma27.c']

# Build PyMA27
ma27_sources = [os.path.join(hsl_rootdir, name) for name in ma27_src]
ma27_sources += [os.path.join('hsl', 'solvers', 'src', name) for name in libma27_src]
pyma27_sources = [os.path.join('hsl', 'solvers', 'src', name) for name in pyma27_src]

if files_exist(ma27_sources):
          
    config.add_library(name='hsl_ma27',
                       sources=ma27_sources,
                       include_dirs=[hsl_rootdir, os.path.join('hsl', 'solvers', 'src')],)



# Build PyMA57
ma57_src = ['ddeps.f', 'ma57d.f']
ma57_sources = [os.path.join(hsl_rootdir, 'ma57d', name) for name in ma57_src]

if files_exist(ma57_sources):
    config.add_library(
            name='hsl_ma57',
            sources=ma57_sources,
            libraries=[metis_lib],
            library_dirs=[metis_dir],
            include_dirs=[hsl_rootdir, os.path.join('hsl', 'solvers', 'src')],)

mc29_sources = [os.path.join(hsl_rootdir, 'mc29d', 'mc29d.f'),
                os.path.join('hsl', 'scaling', 'src', 'mc29.pyf')]

config.add_extension(
        name='scaling._mc29',
        sources=mc29_sources,
        include_dirs=[os.path.join('hsl', 'scaling', 'src')],
        extra_link_args=[])


mc21_sources = [os.path.join(hsl_rootdir,  'mc21d', 'mc21d.f'),
                os.path.join('hsl', 'ordering', 'src', 'mc21.pyf')]

config.add_extension(
        name='ordering._mc21',
        sources=mc21_sources,
        include_dirs=[os.path.join('hsl', 'ordering', 'src')],
        extra_link_args=[])


mc60_sources = [os.path.join(hsl_rootdir, 'mc60d', 'mc60d.f'),
                os.path.join('hsl', 'ordering', 'src', 'mc60.pyf')]

config.add_extension(
        name='ordering._mc60',
        sources=mc60_sources,
        include_dirs=[os.path.join('hsl', 'ordering', 'src')],
        extra_link_args=[])

## Extensions using Cython
ext_params = {}
ext_params['include_dirs'] = include_dirs
if not use_debug_symbols:
    ext_params['extra_compile_args'] = ["-O2", '-std=c99', '-Wno-unused-function']
    ext_params['extra_link_args'] = []
else:
    ext_params['extra_compile_args'] = ["-g", '-std=c99', '-Wno-unused-function']
    ext_params['extra_link_args'] = ["-g"]
       
context_ext_params = copy.deepcopy(ext_params)
cyma27_src_INT32_FLOAT64 = ['ma27_lib.c',
                                          'hsl_alloc.c',
                                          '_cyma27_base_INT32_FLOAT64.c']
cyma27_sources_INT32_FLOAT64 = [os.path.join('hsl', 'solvers', 'src', name) for name in cyma27_src_INT32_FLOAT64]

cyma27_base_ext_params_INT32_FLOAT64 = copy.deepcopy(ext_params)
cyma27_base_ext_params_INT32_FLOAT64['libraries'] = ['hsl_ma27']
retval = os.getcwd()
os.chdir('hsl/solvers/src')
call(['cython', '_cyma27_base_INT32_FLOAT64.pyx'])
os.chdir(retval)
config.add_extension(
            name='solvers.src._cyma27_base_INT32_FLOAT64',
            sources=cyma27_sources_INT32_FLOAT64,
            **cyma27_base_ext_params_INT32_FLOAT64)

retval = os.getcwd()
os.chdir('hsl/solvers/src')
call(['cython', '_cyma27_numpy_INT32_FLOAT64.pyx'])
os.chdir(retval)
cyma27_numpy_ext_params_INT32_FLOAT64 = copy.deepcopy(ext_params)
config.add_extension(name="solvers.src._cyma27_numpy_INT32_FLOAT64",
                 sources=['hsl/solvers/src/_cyma27_numpy_INT32_FLOAT64.c'],
                 **cyma27_numpy_ext_params_INT32_FLOAT64)



cyma57_src_INT32_FLOAT64 = ['ma57_lib.c',
                                          'hsl_alloc.c',
                                          '_cyma57_base_INT32_FLOAT64.c']
cyma57_sources_INT32_FLOAT64 = [os.path.join('hsl', 'solvers', 'src', name) for name in cyma57_src_INT32_FLOAT64]

base_ext_params_INT32_FLOAT64 = copy.deepcopy(ext_params)
base_ext_params_INT32_FLOAT64['library_dirs'] = [metis_dir]
base_ext_params_INT32_FLOAT64['libraries'] = [metis_lib, 'hsl_ma57']
retval = os.getcwd()
os.chdir('hsl/solvers/src')
call(['cython', '_cyma57_base_INT32_FLOAT64.pyx'])
os.chdir(retval)
config.add_extension(
            name='solvers.src._cyma57_base_INT32_FLOAT64',
            sources=cyma57_sources_INT32_FLOAT64,
            **base_ext_params_INT32_FLOAT64)

retval = os.getcwd()
os.chdir('hsl/solvers/src')
call(['cython', '_cyma57_numpy_INT32_FLOAT64.pyx'])
os.chdir(retval)
numpy_ext_params_INT32_FLOAT64 = copy.deepcopy(ext_params)
config.add_extension(name="solvers.src._cyma57_numpy_INT32_FLOAT64",
                 sources=['hsl/solvers/src/_cyma57_numpy_INT32_FLOAT64.c'],
                 **numpy_ext_params_INT32_FLOAT64)


if build_cysparse_ext:
    retval = os.getcwd()
    os.chdir('hsl/solvers/src')
    call(['cython', '-I', cysparse_rootdir[0], '_cyma27_cysparse_INT32_FLOAT64.pyx'])
    os.chdir(retval)
    cyma27_cysparse_ext_params_INT32_FLOAT64 = copy.deepcopy(ext_params)
    cyma27_cysparse_ext_params_INT32_FLOAT64['include_dirs'].extend(cysparse_rootdir)
    config.add_extension(name="solvers.src._cyma27_cysparse_INT32_FLOAT64",
                 sources=['hsl/solvers/src/_cyma27_cysparse_INT32_FLOAT64.c'],
                 **cyma27_cysparse_ext_params_INT32_FLOAT64)

    retval = os.getcwd()
    os.chdir('hsl/solvers/src')
    call(['cython', '-I', cysparse_rootdir[0], '_cyma57_cysparse_INT32_FLOAT64.pyx'])
    os.chdir(retval)
    cyma57_cysparse_ext_params_INT32_FLOAT64 = copy.deepcopy(ext_params)
    cyma57_cysparse_ext_params_INT32_FLOAT64['include_dirs'].extend(cysparse_rootdir)
    config.add_extension(name="solvers.src._cyma57_cysparse_INT32_FLOAT64",
                 sources=['hsl/solvers/src/_cyma57_cysparse_INT32_FLOAT64.c'],
                 **cyma57_cysparse_ext_params_INT32_FLOAT64)


packages_list = ['hsl', 'hsl.ordering', 'hsl.scaling', 'hsl.solvers',
                 'hsl.solvers.src']

CLASSIFIERS = """\
Development Status :: 4 - Beta
Intended Audience :: Science/Research
Intended Audience :: Developers
License :: OSI Approved
Programming Language :: Python
Programming Language :: Cython
Topic :: Software Development
Topic :: Scientific/Engineering
Operating System :: POSIX
Operating System :: Unix
Operating System :: MacOS :: MacOS X
Natural Language :: English
"""

here = path.abspath(path.dirname(__file__))
# Get the long description from the relevant file
with open(path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
    long_description = f.read()

config.make_config_py()

setup(packages=packages_list, zip_safe=False, **config.todict())