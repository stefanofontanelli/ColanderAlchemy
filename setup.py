from setuptools import setup, find_packages
import sys, os

version = '0.1.0a'

setup(name='ColanderAlchemy',
      version=version,
      description="Create a Colander schema reading SQLAlchemy model.",
      long_description="""\
A set of tools to convert SQLAlchemy models into Colander schemas.""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='Colander SQLAlchemy',
      author='Stefano Fontanelli',
      author_email='s.fontanelli@asidev.com',
      url='http://code.asidev.com/colander-alchemy',
      license='MIT',
      packages=find_packages('lib'),
      package_dir={'': 'lib'},
      include_package_data=True,
      zip_safe=True,
      install_requires=['Colander', 'SQLAlchemy'],
      tests_require=['nose >= 0.11'],
      test_suite='test',
      )
