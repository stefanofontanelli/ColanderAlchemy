.. ColanderAlchemy documentation master file, created by
   sphinx-quickstart on Wed Mar  7 18:12:21 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

ColanderAlchemy
===============

`ColanderAlchemy` helps you to auto-generate `Colander
<http://http://docs.pylonsproject.org/projects/colander/en/latest/>`_ schemas
based on `SQLAlchemy <http://www.sqlalchemy.org/>`_ mapped classes.
Schemas produced by `ColanderAlchemy`

`ColanderAlchemy` auto-generates `Colander` schemas according to the 
following rules:

#. The type of the schema is ``colander.MappingSchema``

#. The schema has a ``colander.SchemaNode`` for each ``sqlalchemy.Column``
   in the mapped object:

   * The type of ``colander.SchemaNode`` is based on the type of
     ``sqlalchemy.Column``
    
   * The ``colander.SchemaNode`` use ``validator=colander.OneOf`` when the
     type of ``sqlalchemy.Column`` is ``sqlalchemy.types.Enum``

   * ``colander.SchemaNode`` has ``missing=None`` when the
     ``sqlalchemy.Column`` has ``nullable=True``

   * ``colander.SchemaNode`` has ``missing=colander.required`` when the
     ``sqlalchemy.Column`` has ``nullable=False`` or ``primary_key=True``

   * ``colander.SchemaNode`` has ``missing=VALUE`` and ``default=VALUE`` when
     the ``sqlalchemy.Column`` has ``default=VALUE``

#. The schema has a ``colander.SchemaNode`` for each `relationship` in the
   mapped object:

   * The ``colander.SchemaNode`` instance has ``missing=None``

   * Depending on the nature of the `relationship`, the
     ``colander.SchemaNode`` will either be:

     * An instance of ``colander.Mapping`` for relationships that are
       `Many-to-One` and `One-to-One`

     * An instance of ``colander.Sequence`` containing a ``colander.Mapping``
       for relationships that are `Many-to-Many` and `One-to-Many`

   * For both kinds of relationships:
    
     * The ``colander.Mapping`` instance is built by applying the rules in 
       `rule 2` above against the mapped class being referenced by
       the relationship. This means the ColanderAlchemy mapping will happen
       recursively through your model's `relationships` and `backrefs`
       unless explicitly prevented.

       For example, if you have a class ``Account`` which is features a
       `relationship` with another class ``Contact``, then the ``Contact``
       class will be mapped also.
     
       You should beware of circular relationships, particularly in cases
       of using `backrefs` or `back_populates` within your SQLAlchemy models.
       If you encounter infinite recursion, then consider utilizing
       techniques in :ref:`customization` to clarify the mapping of such
       relationships.


Read the section :ref:`customization` to see how change these rules and how
to customize the Colander schema returned by ColanderAlchemy.

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

