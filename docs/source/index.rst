.. ColanderAlchemy documentation master file, created by
   sphinx-quickstart on Wed Mar  7 18:12:21 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

ColanderAlchemy
===============

`ColanderAlchemy` helps you autogenerating 
`Colander <http://http://docs.pylonsproject.org/projects/colander/en/latest/>`_ 
schemas based on `SQLAlchemy <http://www.sqlalchemy.org/>`_ mapped classes.

`ColanderAlchemy` autogenerates `Colander` schemas following these rules:
    1) type of the schema is ``colander.MappingSchema``,
    2) the schema has a ``colander.SchemaNode`` 
       for each ``sqlalchemy.Column`` in the mapped object:
        * the type of ``colander.SchemaNode`` 
          is based on the type of ``sqlalchemy.Column``,
        * the ``colander.SchemaNode`` use ``validator=colander.OneOf``
          when the type of ``sqlalchemy.Column`` is ``sqlalchemy.types.Enum``,
        * ``colander.SchemaNode`` has ``missing=None`` 
          when the ``sqlalchemy.Column`` has ``nullable=True``,
        * ``colander.SchemaNode`` has ``missing=colander.required`` 
          when the ``sqlalchemy.Column`` has ``nullable=False`` or 
          ``primary_key=True``,
        * ``colander.SchemaNode`` has ``missing=VALUE`` and ``default=VALUE`` 
          when the ``sqlalchemy.Column`` has ``default=VALUE``,
    3) these schema has a ``colander.SchemaNode`` 
       for each `relationship` in the mapped object:
        * the ``colander.SchemaNode`` has ``missing=None``,
        * the type of ``colander.SchemaNode`` is:
            * a ``colander.Mapping``
              for `ManyToOne and OneToOne relationships`,
            * a ``colander.Sequence`` of ``colander.Mapping``
              for `ManyToMany and OneToMany relationships`,
        * for both kind of relationships:
            * the ``colander.Mapping`` is built using `rule 2` 
              on the mapped class referenced by relationship.


Read the section :ref:`customization` to see how change these rules and how to customize
the Colander schema returned by ColanderAlchemy.

Read the section :ref:`examples` to see how use `ColanderAlchemy`.

Read the section :ref:`deform` to see how use `ColanderAlchemy` with Deform.

Contents
--------

.. toctree::
    examples
    deform
    customization
    api


Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
* :ref:`api`

