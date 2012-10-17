.. _customization:

Change auto-generation rules
============================

The default ``Colander`` schema generated using ``SQLAlchemyMapping`` follows
the rules below:

#. It has an `optional` (not required) field for each optional column and for
   each relationship

#. It has a `required` field for each primary key or `not nullable` column

#. It has a `default` field for each column which has a default value

#. It validates ``Enum`` columns using the Colander ``OneOf`` validator

The user can change default behaviour of ``SQLAlchemyMapping`` by specifying
the keyword arguments ``includes``, ``excludes``, and ``nullables``.

Read `tests
<https://github.com/stefanofontanelli/ColanderAlchemy/blob/master/tests.py>`_
to understand how they work.

You can subclass the following ``SQLAlchemyMapping`` methods when you need
more customization:

* ``get_schema_from_col``, which returns a ``colander.SchemaNode`` given a
  ``sqlachemy.schema.Column``

* ``get_schema_from_rel``, which returns a ``colander.SchemaNode`` given a
  ``sqlalchemy.orm.relationship``.
  

Changing auto-generation rules directly in SQLAlchemy models
============================================================

You can customize the Colander schema built by ``ColanderAlchemy`` directly
in the SQLAlchemy models as follow::

    from colanderalchemy import Column
    from colanderalchemy import relationship

    from sqlalchemy import Integer
    from sqlalchemy import Unicode
    from sqlalchemy.ext.declarative import declarative_base

    import colander


    Base = declarative_base()


    class Person(Base):
        __tablename__ = 'person'
        id = Column(sqlalchemy.Integer,
                    primary_key=True,
                    ca_type=colander.Float(),
                    ca_name='ID',
                    ca_title='Person ID',
                    ca_description='The Person identifier.',
                    ca_widget='Empty Widget',
                    ca_include=True)
        name = Column(sqlalchemy.Unicode(128),
                      nullable=False,
                      ca_nullable=True,
                      ca_include=True,
                      ca_default=colander.required)
        surname = Column(sqlalchemy.Unicode(128),
                         nullable=False,
                         ca_exclude=True)

.. _ca-keyword-arguments:

Customizable Keyword Arguments
==============================

``colanderalchemy.Column`` and ``colanderalchemy.relationship`` accept
following keyword arguments that are mapped directly to attributes on
``colander.SchemaNode``: 

    * ``ca_type``,
    * ``ca_children``,
    * ``ca_default``,
    * ``ca_missing``,
    * ``ca_preparer``,
    * ``ca_validator``,
    * ``ca_after_bind``,
    * ``ca_title``, 
    * ``ca_description``,
    * ``ca_widget``.

As an example, the value of the keyword ``ca_title`` will be passed as the
keyword argument ``title`` (the string without the leading ``ca_`` prefix)
when instatiating the ``colander.SchemaNode``. For more information about
what these options can do, see the `Colander
<http://rtd.pylonsproject.org/projects/colander/>`_ documentation.

In addition you can specify:

    * ``ca_include``,
    * ``ca_exclude``,
    * ``ca_nullable``,

These options are useful to either include or exclude attributes from
the resulting ``colander.Schema`` or to make certain nodes nullable.
