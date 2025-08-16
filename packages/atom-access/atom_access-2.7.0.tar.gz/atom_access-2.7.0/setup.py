#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# pylint: disable=line-too-long,missing-module-docstring,exec-used

import setuptools
from textwrap import dedent

with open('README.md', 'r') as file:
    long_description = file.read()

# DO NOT EDIT THIS NUMBER!
# IT IS AUTOMATICALLY CHANGED BY python-semantic-release
__version__ = "2.7.0"

setuptools.setup(
    name='atom_access',
    version=__version__,
    description=dedent(
        'atom_access is a ray tracing package for addressing the steric \
         hindrance of molecules'),
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://gitlab.com/atomaccess/atomaccess",
    project_urls={
        "Bug Tracker": "https://gitlab.com/atomaccess/atomaccess/-/issues",
        "Documentation": "https://atomaccess.gitlab.io/atomaccess/"
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent'
    ],
    packages=setuptools.find_packages(),
    python_requires='>=3.10',
    install_requires=[
        'numpy>=1.24.3',
        'xyz_py>=5.7.0',
        'plotly>=5.14.1',
        'scikit-learn>=1.2.2',
	'pathos>=0.3.4'
    ],
    entry_points={
        'console_scripts': [
            'atom_access = atom_access.cli:main',
            'atomaccess = atom_access.cli:main'
        ]
    }
)
