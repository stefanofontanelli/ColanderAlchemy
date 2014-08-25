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
<https://github.com/stefanofontanelli/ColanderAlchemy/tree/master/tests>`_
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
should be specified like so:

.. code:: python

    name = Column('name', info={'colanderalchemy': {'title': 'Your name',
                                                    'description': 'Test',
                                                    'missing': 'Anonymous',
                                                    ...}
                               })

and you can add any number of other options into the ``dict`` structure as
described above.  So, anything you want passed to the resulting mapped
:class`colander.SchemaNode` should be added here.  This also includes
arbitrary attributes like ``widget``, which, whilst not part of ``Colander`` by
default, is useful for a library like ``Deform``.

Note that for a relationship, these configured attributes will only apply to
the outer mapped :class:`colander.SchemaNode`; this *outer* node being a
:class:`colander.Sequence` or :class:`colander.Mapping`, depending on whether
the SQLAlchemy relationship is x-to-many or x-to-one, respectively. 

To customise the inner mapped class, use the special attribute
``__colanderalchemy_config__`` on the class itself and define this as a
dict-like structure of options that will be passed to
:class:`colander.SchemaNode`, like so:

.. code:: python

    from sqlalchemy.ext.declarative import declarative_base

    Base = declarative_base()

    def address_validator(node, value):
       # Validate address node
       pass

    class Address(Base):
        __colanderalchemy_config__ = {'title': 'An address',
                                      'description': 'Enter an address.',
                                      'validator': address_validator}
        # Other SQLAlchemy columns are defined here



Worked example
--------------

A full worked example could be like this:

.. code:: python

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
                    info={'colanderalchemy': {'typ': colander.Float(),
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

    * ``typ``
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
    * ``children`` - An iterable (such as a list or tuple) of child nodes
      that should be used explicitly rather than mapping the current
      SQLAlchemy aspect.
    * ``name`` - Identifier for the resulting mapped Colander node.
    * ``typ`` - An explicitly-configured Colander node type.


