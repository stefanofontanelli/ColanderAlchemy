from setuptools import setup, find_packages

version = '0.1'

setup(name='ColanderAlchemy',
      version=version,
      description="Autogenerate Colander schemas based on SQLAlchemy models.",
      long_description="""\
An helper tool for autogenerating Colander schemas based on SQLAlchemy mapped classes.""",
      classifiers=['Development Status :: 4 - Beta',
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
            'colander',
            'SQLAlchemy'],
      tests_require=[],
      test_suite='tests',
      )
