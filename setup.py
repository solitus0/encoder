from setuptools import find_packages, setup

setup(
    name="encoder",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)
