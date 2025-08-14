from setuptools import setup, find_packages

setup(
    name="material_fingerprinting_beta",
    version="0.0.1",
    author="Moritz Flaschel",
    author_email="moritz.flaschel@fau.de",
    url="https://github.com/Material-Fingerprinting",
    packages=find_packages(),
    package_data={
        "material_fingerprinting": ["databases/*.npz"],
    },
    install_requires=[
        "matplotlib",
        "numpy",
    ],
)