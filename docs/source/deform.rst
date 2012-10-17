.. _deform:

Examples: using ColanderAlchemy with Deform
===========================================

``Colander`` options can be specified declaratively in ``SQLAlchemy`` models
as shown in the code below::

    from colanderalchemy import Column
    from colanderalchemy import relationship
    from colanderalchemy import SQLAlchemyMapping

    from sqlalchemy import Enum
    from sqlalchemy import ForeignKey
    from sqlalchemy import Integer
    from sqlalchemy import Unicode
    from sqlalchemy.ext.declarative import declarative_base


    Base = declarative_base()


    class Phone(Base):
        __tablename__ = 'phones'

        person_id = Column(Integer, ForeignKey('persons.id'), primary_key=True)
        number = Column(Unicode(128), primary_key=True)
        location = Column(Enum(u'home', u'work'))


    class Person(Base):
        __tablename__ = 'persons'

        id = Column(Integer, primary_key=True)
        name = Column(Unicode(128), nullable=False)
        surname = Column(Unicode(128), nullable=False)
        phones = relationship('Phone')


    person = SQLAlchemyMapping(Person)

The resulting schema from the code above is the same as what would
be produced by constructing the following ``Colander`` schema by hand::

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

This means that geting a ``Deform`` form to use ``ColanderAlchemy`` is 
as simple as using any other ``Colander`` schema::

    from colanderalchemy import SQLAlchemyMapping
    from deform import Form

    # Using Colander
    # person = Person()

    # Using ColanderAlchemy
    person = SQLAlchemyMapping(Person)
    
    form = Form(person, buttons=('submit',))

Keep in mind that if you want additional control over the resulting
``Colander`` schema and nodes produced (such as controlling a node's `title`,
`description`, `widget` or more), you are able to provide appropriate keyword
arguments declaratively within the ``SQLAlchemy`` model. For more
information, see :ref:`customization`.
