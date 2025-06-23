from setuptools import setup, Extension
from Cython.Build import cythonize
import numpy

# Cython extension tanımları
extensions = [
    Extension(
        "accelerated.dna_codec_cy",
        ["accelerated/dna_codec.pyx"],
        include_dirs=[numpy.get_include()],
        extra_compile_args=["-O3", "-ffast-math"],
        extra_link_args=["-O3"]
    ),
    Extension(
        "accelerated.logistic_cy", 
        ["accelerated/logistic.pyx"],
        include_dirs=[numpy.get_include()],
        extra_compile_args=["-O3", "-ffast-math"],
        extra_link_args=["-O3"]
    ),
    Extension(
        "accelerated.chaos_utils_cy",
        ["accelerated/chaos_utils.pyx"],
        include_dirs=[numpy.get_include()],
        extra_compile_args=["-O3", "-ffast-math"],
        extra_link_args=["-O3"]
    ),
]

setup(
    name="chaos_crypto_cython",
    ext_modules=cythonize(extensions, compiler_directives={
        'language_level': 3,
        'boundscheck': False,
        'wraparound': False,
        'cdivision': True,
        'nonecheck': False,
        'initializedcheck': False,
    }),
    zip_safe=False,
)