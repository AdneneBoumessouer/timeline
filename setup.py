#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 27 14:40:39 2021

@author: aboumessouer
"""

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ProductionPlaner",
    version="1.0.0",
    author="aboumessouer",
    author_email="a.boumessouer@fm-maschinenbau.de",
    description="Creates a reference production plan of upcoming jobs specified by the user.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.int.fm-maschinenbau.de/smartblick/students/productionplanpredictor",
    packages=setuptools.find_packages(exclude=["tests"]),
    install_requires=[
        "DateTimeRange==1.0.0",
        "pandas==1.1.3",
        "numpy==1.19.2",
        "plotly==4.14.3",
        "hypothesis==6.7.0",
    ],
    classifiers=[
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
