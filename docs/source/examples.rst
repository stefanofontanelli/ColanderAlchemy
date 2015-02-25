.. _examples:

Examples
========

Less boilerplate
----------------

The best way to illustrate the benefit of using ColanderAlchemy is to
show a comparison between the code required to represent SQLAlchemy
model as a Colander schema.

Suppose you have these SQLAlchemy mapped classes::

.. code-block:: python

    from sqlalchemy import Column, Enum, ForeignKey, Integer, Unicode
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import relationship


    Base = declarative_base()


    class Phone(Base):
        __tablename__ = 'phones'

        person_id = Column(Integer, ForeignKey('persons.id'), primary_key=True)
        number = Column(Unicode(128), primary_key=True)
        location = Column(Enum('home', 'work'))

    class Friend(Base):
        __tablename__ = 'friends'

        person_id = Column(Integer, ForeignKey('persons.id'), primary_key=True)
        friend_of = Column(Integer, ForeignKey('persons.id'), primary_key=True)
        rank = Column(Integer, default=0)
    
    class Person(Base):
        __tablename__ = 'persons'

        id = Column(Integer, primary_key=True)
        name = Column(Unicode(128), nullable=False)
        surname = Column(Unicode(128), nullable=False)
        gender = Column(Enum('M', 'F'))
        age = Column(Integer)
        phones = relationship(Phone)
        friends = relationship(Friend, foreign_keys=[Friend.person_id])


The code you need to create the Colander schema for ``Person`` would be::

.. code-block:: python

    import colander


    class Friend(colander.MappingSchema):
        person_id = colander.SchemaNode(colander.Int())
        friend_of = colander.SchemaNode(colander.Int())
        rank = colander.SchemaNode(colander.Int(), 
                                   missing=0, 
                                   default=0)


    class Phone(colander.MappingSchema):
        person_id = colander.SchemaNode(colander.Int())
        number = colander.SchemaNode(colander.String(),
                                     validator=colander.Length(0, 128))
        location = colander.SchemaNode(colander.String(),
                                       validator=colander.OneOf(['home', 'work']),
                                       missing=colander.drop)


    class Friends(colander.SequenceSchema):
        friends = Friend(missing=colander.drop)


    class Phones(colander.SequenceSchema):
        phones = Phone(missing=colander.drop)


    class Person(colander.MappingSchema):
        id = colander.SchemaNode(colander.Int(),
                                 missing=colander.drop)
        name = colander.SchemaNode(colander.String(),
                                   validator=colander.Length(0, 128))
        surname = colander.SchemaNode(colander.String(),
                                      validator=colander.Length(0, 128))
        gender = colander.SchemaNode(colander.String(),
                                     validator=colander.OneOf(['M', 'F']),
                                     missing=colander.drop)
        age = colander.SchemaNode(colander.Int(), 
                                  missing=colander.drop)
        phones = Phones(missing=colander.drop)
        friends = Friends(missing=colander.drop)


    person = Person()


By contrast, all you need to obtain the same Colander schema for the
``Person`` mapped class using ColanderAlchemy is simply::

.. code-block:: python

    from colanderalchemy import setup_schema

    setup_schema(None, Person)
    schema = Person.__colanderalchemy__


Or alternatively, you may do this::

.. code-block:: python

    from colanderalchemy import SQLAlchemySchemaNode

    schema = SQLAlchemySchemaNode(Person)


As you can see, it's a lot simpler.
