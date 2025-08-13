#!/usr/bin/env python3

from setuptools import setup

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='symlink',
    version='0.0.0',
    license='MIT',
    author='nggit',
    author_email='contact@anggit.com',
    description=(
        'Initial symlink package.'
    ),
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/nggit/symlink',
    packages=['symlink'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries',
    ],
)
