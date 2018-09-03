
import sys
from distutils.core import setup, Extension

setup(
    name='rubikscubennnsolver',
    version='1.0.0',
    description='Resolve rubiks cube NxNxN solver',
    keywords='rubiks cube NxNxN solver',
    url='https://github.com/dwalton76/rubiks-cube-solvers/tree/master/NxNxN',
    author='Daniel Walton',
    author_email='dwalton76@gmail.com',
    license='GPLv3',
    scripts=['usr/bin/rubiks-cube-solver.py'],
    packages=['rubikscubennnsolver'],
)

