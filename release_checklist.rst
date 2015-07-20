
RELEASE CHECKLIST
=================

- update version to release version
   - setup.py
   - CHANGES.rst *(add release date)*
   - docs/source/conf.py
- commit version changes to git
- tag last commit with version number
   - ``git tag -a [version number]``
- build distributions:
   - ``python setup.py sdist``
   - ``python setup.py bdist_wheel``
- upload to pypi
   - ``python setup.py register``
   - ``python setup.py sdist upload``
   - ``python setup.py bdist_wheel upload``
- confirm README contents and such are properly rendered on PyPI.
  If rendering is incorrect, test RST files with an RST parsing
  program to test for bugs. (http://rst.ninjs.org/ will give error
  messages)


POST-RELEASE CHECKLIST
======================

- update version to development version
   - setup.py
   - CHANGES.rst
   - docs/source/conf.py
- commit version changes to git

