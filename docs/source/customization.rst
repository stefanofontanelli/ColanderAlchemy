.. _customization:

Customization
=============

Changing auto-generation rules
------------------------------

The default ``Colander`` schema generated using
:class:`colanderalchemy.SQLAlchemySchemaNode` follows certain rules seen in
:ref:`how_it_works`.  You can change the default behaviour of
:class:`colanderalchemy.SQLAlchemySchemaNode` by specifying the keyword
arguments ``includes``, ``excludes``, and ``overrides``.  

Refer to the API for :class:`colanderalchemy.SQLAlchemySchemaNode` and the
`tests
<https://github.com/stefanofontanelli/ColanderAlchemy/blob/master/tests.py>`_
to understand how they work.

This class also accepts all keyword arguments that could normally be passed to
a basic :class:`colander.SchemaNode`, such as `title`, `description`,
`preparer`, and more. Read more about basic Colander customisation at
http://docs.pylonsproject.org/projects/colander/en/latest/basics.html.

If the available customisation isn't sufficient, then you can subclass the
following :class:`colanderalchemy.SQLAlchemySchemaNode` methods when you need
more control:

* :meth:`SQLAlchemySchemaNode.get_schema_from_column`, which
  returns a ``colander.SchemaNode`` given a ``sqlachemy.schema.Column``

* :meth:`SQLAlchemySchemaNode.get_schema_from_relationship`,
  which returns a ``colander.SchemaNode`` given a
  ``sqlalchemy.orm.relationship``.
  

.. _info_argument:

Configuring within SQLAlchemy models
------------------------------------

One of the most useful aspects of ``ColanderAlchemy`` is the ability to
customize the schema being built by including hints directly in your
``SQLAlchemy`` models. This means you can define just one ``SQLAlchemy``
model and have it translate to a fully-customised ``Colander`` schema, and
do so purely using declarative code.  Alternatively, since the resulting schema
is just a :class:`colander.SchemaNode`, you can configure it imperatively too,
if you prefer.

``Colander`` options can be specified declaratively in ``SQLAlchemy`` models
using the ``info`` argument that you can pass to either
:class:`sqlalchemy.Column` or :meth:`sqlalchemy.orm.relationship`.  ``info``
accepts any and all options that :class:`colander.SchemaNode` objects do and
should be specified like so::

    name = Column('name', info={'colanderalchemy': {'title': 'Your name',
                                                    'description': 'Test',
                                                    'missing': 'Anonymous',
                                                    ...}
                               })

and you can add any number of other options into the ``dict`` structure as
described above.  So, anything you want passed to the resulting mapped
:class`colander.SchemaNode` should be added here.  This also includes
things like ``widget``, which, whilst not part of ``Colander`` by default, is
useful for a library like ``Deform``.

A full worked example could be like this::

    from sqlalchemy import Integer
    from sqlalchemy import Unicode
    from sqlalchemy.ext.declarative import declarative_base

    import colander


    Base = declarative_base()


    class Person(Base):
        __tablename__ = 'person'
        #Fully customised schema node
        id = Column(sqlalchemy.Integer,
                    primary_key=True,
                    info={'colanderalchemy': {'type': colander.Float(),
                                              'name': 'ID',
                                              'title': 'Person ID',
                                              'description': 'The Person identifier.',
                                              'widget': 'Empty Widget'}})
        #Explicitly set as a default field
        name = Column(sqlalchemy.Unicode(128),
                      nullable=False,
                      info={'colanderalchemy': {'default': colander.required}})
        #Explicitly excluded from resulting schema
        surname = Column(sqlalchemy.Unicode(128),
                         nullable=False,
                         info={'colanderalchemy': {'exclude': True}})


.. _ca-keyword-arguments:

Customizable Keyword Arguments
------------------------------

``sqlalchemy.Column`` and ``sqlalchemy.orm.relationship`` can be configured
with an ``info`` argument that ``ColanderAlchemy`` will use to customise
resulting :class:`colander.SchemaNode` objects for each attribute.  The
special (magic) key for attributes is ``colanderalchemy``, so a Column 
definition should look like how it was mentioned above in :ref:`info_argument`.

This means you can customise options like:

    * ``type``
    * ``children``
    * ``default``
    * ``missing``
    * ``preparer``
    * ``validator``
    * ``after_bind``
    * ``title``
    * ``description``
    * ``widget``

Keep in mind the above list isn't exhaustive and you should
refer to the complete documentation at 
http://docs.pylonsproject.org/projects/colander/en/latest/basics.html.

So, as an example, the value of ``title`` will be passed as the keyword argument
``title`` when instantiating the ``colander.SchemaNode``. For more information
about what each of the options can do, see the `Colander
<http://rtd.pylonsproject.org/projects/colander/>`_ documentation.

In addition, you can specify the following custom options to control
what ``ColanderAlchemy`` itself does:

    * ``exclude`` - Boolean value for whether to exclude a given attribute.
      Extremely useful for keeping a ``Column`` or ``relationship`` out of
      a schema.  For instance, an internal field that shouldn't be made
      available on a ``Deform`` form.
    * ``children`` - XXX
    * ``name`` - XXX
    * ``typ`` - XXX


