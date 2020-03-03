Change Log
==========

0.3.4 (2020-03-03)
-----------------------

- no functional changes; updates to tests and supported versions

0.3.3 (2015-07-20)
------------------

- Allow recursive schema creation (PR `#81 <https://github.com/stefanofontanelli/ColanderAlchemy/pull/81>`_).
  [Ademan, offlinehacker]
- Allow ``includes``, ``excludes`` and ``overrides`` to be specified in
  ``__colanderalchemy_config__`` and applied to the ``SchemaNode``.
  [davidjb]
- Clarify documentation for quickstart.
  [davidjb]

0.3.2.post1 (2015-03-11)
------------------------

- Only apply declaratively defined settings to the outer Sequence when
  mapping an SQLAlchemy relationship. Previously, overrides were applied
  to both the Sequence and Mapping nodes, leading to unexpected behaviour.
  [davidjb]
- The order in which fields are added are now properly maintained
  (`issue #45
  <https://github.com/stefanofontanelli/ColanderAlchemy/issues/45>`_)
  [uralbash]
- Added ability to override fields on their own (PR
  `#69 <https://github.com/stefanofontanelli/ColanderAlchemy/pull/69>`_,
  `#70 <https://github.com/stefanofontanelli/ColanderAlchemy/pull/70>`_)
  [uralbash]
- Allow setting ColanderAlchemy options in sqlalchemy type. [pieterproigia]
- Make it possible to set the ``unknown`` ``colander.Mapping`` option
  using ``__colanderalchemy_config__`` (PR
  `#78 <https://github.com/stefanofontanelli/ColanderAlchemy/pull/78>`_)
  [elemoine]

0.3.1 (2014-03-19)
------------------

- maintain the order of SQLAlchemy object attributes in the
  Colander schema [tisdall]
- use Colander defaults wherever explicit settings are
  not given [tisdall]
- added tests for confirming documentation examples [tisdall]
- added fix and test for `issue #35
  <https://github.com/stefanofontanelli/ColanderAlchemy/issues/35>`_
  (thrown exception on encountering synonym() ) [tisdall]
- made changes to accommodate SQLAlchemy >= 0.9a [tisdall]
- allows "children" override
  (`issue #44
  <https://github.com/stefanofontanelli/ColanderAlchemy/issues/44>`_)
  [tisdall]
- no longer call callable SQLAlchemy defaults to fill in
  colander default values (`issue #43
  <https://github.com/stefanofontanelli/ColanderAlchemy/issues/43>`_)
  [tisdall]
- fixed some minor issues with colander default and missing values
  to ensure transitive relationships (such as dictify/objectify)
  [tisdall]
- require colander 1.0b1 or greater to support `colander.drop`
  (`issue #52
  <https://github.com/stefanofontanelli/ColanderAlchemy/issues/52>`_)
  [tisdall]

0.3 (2013-11-04)
----------------

- Add ``objectify`` function on ``SQLAlchemySchemaNode`` -- use this to
  recreate SQLAlchemy object instances from the configured mappers.
  This new method is the opposite of ``dictify``.
  [davidjb]
- Colander's ``DateTime`` now defaults to using a naive ``datetime``
  when no timezone is provided, similar to SQLAlchemy.
  [tisdall]
- fixed defaults for SchemaNode.default and SchemaNode.missing
  [tisdall]

0.2 (2013-05-16)
----------------

- No changes.

0.2a1 (2012-04-09)
------------------

- Ensure relationship mapped schemas have a ``name``. This ensures
  correct usage with ``Deform``.
- Ensure missing schema node information correctly maps to SQLAlchemy
  structures.
- Map missing information for "required" relationships based upon the
  join condition. This can be further customised by given relationships
  setting ``missing=colander.required`` within their respective
  configurations.
- Read Colander node init settings for a mapped class using the
  ``__colanderalchemy__`` attribute.  This allows for full customisation
  of the resulting ``colander.Mapping`` SchemaNode.
- Allow non-SQLAlchemy schema nodes within ``SQLAlchemySchemaNode``.
  Previously, the ``dictify`` method would throw an ``AttributeError``.
- Fix setup.py for python 3k

0.1b7 (Unreleased)
------------------

- Ensure relationships are mapped recursively and adhere to
  ColanderAlchemy settings for mappings.
- Remove dictify method in SQLAlchemyMapping.

0.1b6 (2012-10-17)
------------------

- Fix minor bugs.

0.1b5 (2012-09-19)
------------------

- Fix bug in MappingRegistry.__init__:
  pkeys is a list of property keys instead of column name
- Add support to specify schema node ordering.

0.1b4 (2012-08-06)
------------------

- Fix bug related to 'ca_include=False'.
- Change tests to cover that bug.

0.1b3 (2012-08-02)
------------------

- Fix issue related to mapped class inheritance.
- Fix minor bugs.

0.1b2 (2012-06-14)
------------------

- Added support to use ColanderAlchemy declaratively.

0.1b (2012-05-19)
-----------------

- Added SQLAlchemyMapping.dictify method.
- Updated tests with checks needed to test SQLAlchemyMapping.dictify.

0.1.0a2 (unreleased)
--------------------

- Mentioned supported Python versions in trove classifiers.
- Updated tests to run with current `colander` versions.
- Made compatible with Python 3.2.

0.1.0a (2012-03-24)
-------------------

- Initial public release.
