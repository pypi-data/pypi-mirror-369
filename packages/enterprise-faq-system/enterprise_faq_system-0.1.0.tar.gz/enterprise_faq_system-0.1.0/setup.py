from setuptools import setup, find_packages

# Read dependencies from pyproject.toml is handled automatically
setup(
    packages=find_packages(),
    include_package_data=True,
)