import os
import sys
from setuptools import setup, find_packages

version = '0.3.1dev'

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

if sys.version_info[0] == 2 and sys.version_info[1] < 7:
    # In Python < 2.7 use unittest2.
    tests_require=['unittest2']
else:
    tests_require=[]

setup(name='ColanderAlchemy',
      version=version,
      description="Autogenerate Colander schemas based on SQLAlchemy models.",
      long_description=README + '\n\n' + CHANGES,
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2.6',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3.2',
                   'Programming Language :: Python :: 3.3',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: OS Independent',
                   'Topic :: Database'],
      keywords='serialize deserialize validate schema validation colander sqlalchemy',
      author='Stefano Fontanelli',
      author_email='s.fontanelli@asidev.com',
      url='https://github.com/stefanofontanelli/ColanderAlchemy',
      license='MIT',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
            'colander >= 0.9.8',
            'SQLAlchemy >= 0.8dev'],
      tests_require=tests_require,
      test_suite='tests',
      )
