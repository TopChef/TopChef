#!/usr/bin/env python

from setuptools import setup

setup(name='topchef',
      version='0.1',
      description='Python library for running remote computing jobs',
      author='Michal Kononenko',
      author_email='mkononen@uwaterloo.ca',
      packages=['topchef'],
      install_requires=[
          'Flask==0.12.2',
          'jsonschema==2.6.0',
          'marshmallow==2.13.5',
          'marshmallow-jsonschema==0.3.0',
          'pytz==2017.2',
          'SQLAlchemy==1.1.10',
          'sqlalchemy-migrate==0.11.0'
      ]
)
