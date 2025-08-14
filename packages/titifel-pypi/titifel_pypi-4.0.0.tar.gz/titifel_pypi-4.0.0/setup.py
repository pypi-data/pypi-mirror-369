from setuptools import setup, find_packages

setup(
    name="titifel-pypi",
    version="4.0.0",
    packages=find_packages(),
    install_requires=[],
    entry_points={
    "console_scripts": [
        "titifel-info=titifel_pypi.collect_info:main",
    ],
},
)

