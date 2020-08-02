from setuptools import setup

with open("README.md") as fh:
    readme_text = fh.read()

with open("LICENSE") as fh:
    license_text = fh.read()

setup(
    name="rubikscubennnsolver",
    version="1.0.0",
    description="Resolve rubiks cube NxNxN solver",
    long_description=readme_text,
    keywords="rubiks cube NxNxN solver",
    url="https://github.com/dwalton76/rubiks-cube-solvers/tree/master/NxNxN",
    author="Daniel Walton",
    author_email="dwalton76@gmail.com",
    license=license_text,
    scripts=["usr/bin/rubiks-cube-solver.py"],
    packages=["rubikscubennnsolver"],
)
