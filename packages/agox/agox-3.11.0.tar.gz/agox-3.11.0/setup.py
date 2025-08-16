from setuptools import setup  # noqa
from setuptools.extension import Extension
from Cython.Build import cythonize
import numpy

extensions = [
    Extension(
        name="agox.models.GPR.priors.repulsive",
        sources=["agox/models/GPR/priors/repulsive.pyx"],
        include_dirs=[numpy.get_include()],
    ),
    Extension(
        name="agox.models.descriptors.fingerprint_cython.angular_fingerprintFeature_cy",
        sources=["agox/models/descriptors/fingerprint_cython/angular_fingerprintFeature_cy.pyx"],
        include_dirs=[numpy.get_include()],
    ),
]

setup(
    ext_modules=cythonize(extensions),
)
