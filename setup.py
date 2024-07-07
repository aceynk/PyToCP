from setuptools import setup, find_packages

setup(
    name="pytocp",
    version="1.0.0",
    packages=find_packages(where='src'),
    package_dir={'':'src'}
)