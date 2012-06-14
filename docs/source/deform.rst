.. _deform:

Examples: using ColanderAlchemy with Deform.
========

Colander options can be specified declaratively in SQLAlchemy models as shown in code below::

    from colanderalchemy import Column
    from colanderalchemy import relationship

    from sqlalchemy import Enum
    from sqlalchemy import ForeignKey
    from sqlalchemy import Integer
    from sqlalchemy import Unicode
    from sqlalchemy.ext.declarative import declarative_base


    Base = declarative_base()


    class Person(Base):
        __tablename__ = 'persons'

        id = Column(Integer, primary_key=True)
        name = Column(Unicode(128), nullable=False)
        surname = Column(Unicode(128), nullable=False)
        phones = relationship('Phone')


    class Phone(Base):
        __tablename__ = 'phones'

        person_id = Column(Integer, ForeignKey('persons.id'), primary_key=True)
        number = Column(Unicode(128), primary_key=True)
        location = Column(Enum(u'home', u'work'))


The code above is the same of::

    import colander


    class Phone(colander.MappingSchema):
        person_id = colander.SchemaNode(colander.Int())
        number = colander.SchemaNode(colander.String(),
                                     colander.Length(0, 128))
        location = colander.SchemaNode(colander.String(),
                                       validator=colander.OneOf(['home', 'work']),
                                       missing=None)


    class Phones(colander.SequenceSchema):
        phone = Phone()


    class Person(colander.MappingSchema):
        id = colander.SchemaNode(colander.Int())
        name = colander.SchemaNode(colander.String(),
                                   colander.Length(0, 128))
        surname = colander.SchemaNode(colander.String(),
                                      colander.Length(0, 128))
        phones = Phones(missing=[], default=[])


Getting a Deform form using ColanderAlchemy is simple as using Colander::

    from colanderalchemy import SQLAlchemyMapping
    from deform import Form

    # Using Colander
    # person = Person()

    # Using ColanderAlchemy
    person = SQLAlchemyMapping(Person)
    
    form = Form(person, buttons=('submit',))

