# -*- coding: utf-8 -*-

# Borrowed from: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='pubmark',
    version='0.1.0',
    description='A collection of tools for a faster publishing of books with markdown',
    long_description=readme,
    author='Matej Stavanja',
    author_email='matej@stavanja.io',
    url='https://github.com/rabarbara/publish-with-markdown.git',
    license=license,
    packages=find_packages(exclude=('tests', 'docs'))
)