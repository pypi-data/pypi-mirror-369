from setuptools import setup, find_packages

setup(
    name="titifel_pypi",
    version="5.0.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.0",
    ],
)
