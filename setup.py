import os
from setuptools import setup, find_packages

version = '0.3.dev0'

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

setup(name='ColanderAlchemy',
      version=version,
      description="Autogenerate Colander schemas based on SQLAlchemy models.",
      long_description=README + '\n\n' + CHANGES,
      classifiers=['Development Status :: 3 - Alpha',
                   'Intended Audience :: Developers',
                   'Programming Language :: Python',
                   'Programming Language :: Python :: 2.6',
                   'Programming Language :: Python :: 2.7',
                   'Programming Language :: Python :: 3.2',
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
      tests_require=[],
      test_suite='tests',
      )
