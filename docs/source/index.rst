.. ColanderAlchemy documentation master file, created by
   sphinx-quickstart on Wed Mar  7 18:12:21 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

ColanderAlchemy
===============

`ColanderAlchemy` helps you to automatically generate
`Colander <http://docs.pylonsproject.org/projects/colander/>`_
schemas based on `SQLAlchemy <http://www.sqlalchemy.org/>`_ mapped classes.

Quick start
-----------

In order to get started with `ColanderAlchemy`, you can either use
:meth:`colanderalchemy.setup_schema` to automatically create and attach a
schema to a mapped class for you, or else you can use
:class:`colanderalchemy.SQLAlchemySchemaNode` to have more control over the
auto-generated schema.

The easiest way to get going is to set up an SQLAlchemy event listener.
The :meth:`colanderalchemy.setup_schema` method is designed to be attached to
the ``mapper_configured`` event:

.. code-block:: python

    from sqlalchemy import event
    from colanderalchemy import setup_schema
    event.listen(mapper, 'mapper_configured', setup_schema)

Now, once you configure any mapped class, you'll automatically get a mapped
Colander schema on the class as the attribute ``__colanderalchemy__``.
Keep in mind that you should configure the event listener as soon as possible
in your application, especially if you're using `declarative
<http://docs.sqlalchemy.org/en/latest/orm/extensions/declarative/>`_
definitions.

By associating ``ColanderAlchemy`` configuration with your mapped class,
its columns, and its relationships, you can tell ``ColanderAlchemy``
how to generate each and every part of your mapped schema - including things
like titles, descriptions, preparers, validators, widgets, and more. 

Check out :ref:`info_argument` for more information on how.

Usage
-----

Beyond the event listener methodology above, you can use
:meth:`colanderalchemy.setup_schema` manually.  Simply pass it a SQLAlchemy
mapped class like so:

.. code-block:: python

   from sqlalchemy import Column, Integer, String, Text
   from sqlalchemy.ext.declarative import declarative_base
   from colanderalchemy import setup_schema
   
   Base = declarative_base()

   class SomeClass(Base):
       __tablename__ = 'some_table'
       id = Column(Integer, primary_key=True)
       name =  Column(String(50))
       biography =  Column(Text())

   setup_schema(None, SomeClass)
   SomeClass.__colanderalchemy__  # A Colander schema for you to use

If you already have a mapped class available, you can just pass it as is - you
don't need to redefine another schema. 

Also, if you'd like even more control over your generated schema, then
use :class:`colanderalchemy.SQLAlchemySchemaNode` directly like so:

.. code-block:: python

    from colanderalchemy import SQLAlchemySchemaNode
    from my.project import SomeClass

    schema = SQLAlchemySchemaNode(SomeClass,
                                  includes=['name', 'biography'],
                                  excludes=['id'],
                                  title='Some class') 

Or include custom field:

.. code-block:: python

    import deform
    import colander
    from colanderalchemy import SQLAlchemySchemaNode
    from my.project import SomeClass

    typ = colander.String()
    widget = deform.widget.SelectWidget(values=(('foo', 'a'),
                                                ('bar', 'b'),
                                                ('baz', 'c')))
    column = colander.SchemaNode(typ,
                                 name='customfield',
                                 widget=widget)
    schema = SQLAlchemySchemaNode(SomeClass,
                                  includes=['name', column, 'biography'],
                                  excludes=['id'],
                                  title='Some class')

Note the various arguments you can pass when creating your mapped schema -
you have full control over how the schema is generated and what fields
are included, which are excluded, and more. See the
:class:`colanderalchemy.SQLAlchemySchemaNode` API documentation for more
information. For more information you should read the section :ref:`examples`
to see how use `ColanderAlchemy`.

In either situation, you can now pass the resulting ``Colander`` schema to
anything that needs it.  For instance, this works well with ``Deform`` and you
can read more about this later in this documentation: :ref:`deform`.


.. _how_it_works:

How it works
------------

`ColanderAlchemy` auto-generates `Colander` schemas following these rules:

    1) The type of the schema is ``colander.MappingSchema``,

    2) The schema has a ``colander.SchemaNode`` for each ``sqlalchemy.Column``
       in the mapped object:

        * The type of ``colander.SchemaNode`` 
          is based on the type of ``sqlalchemy.Column``
        * The ``colander.SchemaNode`` has a validator if the ``sqlalchemy.Column``
          is an instance of either ``sqlalchemy.types.Enum`` or 
          ``sqlalchemy.types.String``.  ``Enum`` is checked with ``colander.OneOf``
          and ``String`` is checked with ``colander.Length``
        * ``colander.SchemaNode`` has ``missing=colander.required`` except for
          the when ``default`` is set, ``nullable=True``, there's a ``server_default``,
          or the field is an auto incrementing integer used as part of a primary key.
          Essentially it's required unless SQLAlchemy can derive a value for you 
          automatically if it's missing.
        * ``colander.SchemaNode`` has ``default=colander.null`` unless there is
          a column default which is a static scalar value.  Callable function defaults
          and server defaults are ignored for the purposes of generating a 
          colander schema
        * Customisations to the resulting ``colander.SchemaNode`` are applied,
          if defined as part of the ``info`` structure on the
          ``sqlalchemy.Column``.

    3) The schema has a ``colander.SchemaNode`` for each `relationship`
       (``sqlalchemy.orm.relationship`` or those from
       ``sqlalchemy.orm.backref``) in the mapped object:

        * The ``colander.SchemaNode`` has ``missing=None``
        * The type of ``colander.SchemaNode`` is:
            * A ``colander.Mapping`` for `ManyToOne` and `OneToOne`
              relationships
            * A ``colander.Sequence`` of ``colander.Mapping`` for `ManyToMany`
              and `OneToMany` relationships
            * Customisations to the resulting ``colander.SchemaNode`` are
              applied, if defined as part of the ``info`` structure on the
              ``sqlalchemy.orm.relationship``.

        For both kind of relationships, the ``colander.Mapping`` is
        built recursively by applying this same set of rules to the mapped class
        referenced by the relationship.

    4) Customisations to the resulting ``Colander`` schema are applied using
       configuration stored in the ``__colanderalchemy_config__`` attribute
       on the class definition.

Read the section :ref:`customization` to see how change these rules and how to
customize the Colander schema returned by ColanderAlchemy.

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

