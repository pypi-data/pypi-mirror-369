from setuptools import setup, find_packages
from os import path

working_directory = path.abspath(path.dirname(__file__))

with open(path.join(working_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pokedex_python',
    version='0.0.2',
    url='https://github.com/Ishan-Karpe/Pokedex',
    author='Ishan Karpe',
    author_email='ishan.k.abhijeet@gmail.com',
    description="A simple Python Pokédex implementation.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[],
)
