#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='topchef',
    version='0.2',
    description='Python library for running remote computing jobs',
    author='Michal Kononenko',
    author_email='mkononen@uwaterloo.ca',
    packages=find_packages(exclude=['tests.*']),
    install_requires=[
        'Flask==0.12.2',
        'jsonschema==2.6.0',
        'marshmallow==2.13.6',
        'marshmallow-jsonschema==0.4.0',
        'SQLAlchemy==1.3.0',
        'Flask-Script==2.0.5'
    ]
)
