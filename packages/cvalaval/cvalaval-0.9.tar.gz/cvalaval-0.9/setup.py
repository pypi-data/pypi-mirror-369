from setuptools import setup, find_packages

setup(
    name='cvalaval',
    version='0.9',
    packages=find_packages(),
    description='Fast math computations and helpers',
    author='Airwolftomato',
    python_requires='>=3.7',
    install_requires=[
        'gmpy2',
    ],
)