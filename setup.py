# File needed to build Cython modules

# To compile :
#   python setup.py build_ext --inplace

from distutils.core import setup, Extension
from Cython.Distutils import build_ext
import numpy as np

setup(
    name = "clibPhase",
    version = "0.1",

    ext_modules = [Extension('clibPhase',
                                ['clibPhase.pyx'],
                                include_dirs=[np.get_include()])],

    cmdclass = {'build_ext': build_ext}
)
