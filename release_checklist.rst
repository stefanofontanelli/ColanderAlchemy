
RELEASE CHECKLIST
=================

- update version to release version
   - setup.py
   - CHANGES.rst *(add release date)*
   - docs/source/conf.py
- commit version changes to git and push to github
- go to https://github.com/stefanofontanelli/ColanderAlchemy/releases
  and "Draft a new release" with the tag and title being
  "v[verion number]"
- build distributions:
   - ``pip install wheel``
   - ``python setup.py sdist bdist_wheel``
- upload to pypi
   - have 'twine' installed with pypi API token in ~/.pypirc
   - ``twine upload dist/*``
- confirm README contents and such are properly rendered on PyPI.
  If rendering is incorrect, test RST files with an RST parsing
  program to test for bugs. (http://rst.ninjs.org/ will give error
  messages)


POST-RELEASE CHECKLIST
======================

- update version to development version (increment and add '.dev1')
   - setup.py
   - CHANGES.rst
   - docs/source/conf.py
- commit version changes to git

