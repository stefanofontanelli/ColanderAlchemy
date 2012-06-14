.. _customization:

Change autogeneration rules
===========================

Default Colander schema generated using SQLAlchemyMapping follows the rules below:
    1) it has a not required field for each not required column and for each relationship,
    2) it has a required field for each primary key or not nullable column,
    3) it has a default field for each column which has a default value,
    4) it validates ``Enum`` columns using Colander ``OneOf`` validator.

The user can change default behaviour of SQLAlchemyMapping specifing keyword arguments 
``includes`` or ``excludes`` and ``nullables``.

Read `tests <https://github.com/stefanofontanelli/ColanderAlchemy/blob/master/tests.py>`_ to understand how they work.

You can subclass SQLAlchemyMapping methods ``get_schema_from_col`` and ``get_schema_from_rel``
when you need more customization.


Change autogeneration rules directly in SQLAlchemy models
=========================================================

You can customize the Colander schema built by ColanderAlchemy directly in the SQLAlchemy models as follow::

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

``colanderalchemy.Column`` and ``colanderalchemy.relationship`` accept following keyword arguments that are mapped directly on ``Colander.SchemaNode`` ones:
    * ``ca_type``,
    * ``ca_children``,
    * ``ca_name``,
    * ``ca_default``,
    * ``ca_missing``,
    * ``ca_preparer``,
    * ``ca_validator``,
    * ``ca_after_bind``,
    * ``ca_title``, 
    * ``ca_description``,
    * ``ca_widget``.

In addition you can specify:
    * ``ca_include``,
    * ``ca_exclude``,
    * ``ca_nullable``,

that are usefull to include/exclude attributes or made them nullable.
