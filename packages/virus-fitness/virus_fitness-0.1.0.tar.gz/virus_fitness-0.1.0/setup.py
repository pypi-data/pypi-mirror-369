from setuptools import setup, find_packages

setup(
    name='virus_fitness',
    version='0.1.0',
    description='A package for virus fitness estimation using MLR model',
    author='USER01',
    packages=find_packages(),
    install_requires=[
        'pandas',
        'numpy',
        'tensorflow',
        'matplotlib',
    ],
    python_requires='>=3.7',
)
