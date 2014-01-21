.. _deform:

Examples: using ColanderAlchemy with Deform
===========================================

When using ``ColanderAlchemy``, the resulting ``Colander`` schema will
reflect the configuration on the mapped class, as shown in the code below::

    from colanderalchemy import SQLAlchemySchemaNode

    from sqlalchemy import Enum, ForeignKey, Integer, Unicode
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
        phones = relationship(Phone)


    schema = SQLAlchemySchemaNode(Person)

The resulting schema from the code above is the same as what would
be produced by constructing the following ``Colander`` schema by hand::

    import colander


    class Phone(colander.MappingSchema):
        person_id = colander.SchemaNode(colander.Int(), 
                                        missing=colander.drop)
        number = colander.SchemaNode(colander.String(),
                                     validator=colander.Length(0, 128))
        location = colander.SchemaNode(colander.String(),
                                       validator=colander.OneOf(['home', 'work']),
                                       missing=None)


    class Phones(colander.SequenceSchema):
        phones = Phone(missing=[])


    class Person(colander.MappingSchema):
        id = colander.SchemaNode(colander.Int(), missing=colander.drop)
        name = colander.SchemaNode(colander.String(),
                                   validator=colander.Length(0, 128))
        surname = colander.SchemaNode(colander.String(),
                                      validator=colander.Length(0, 128))
        phones = Phones(missing=[])


    schema = Person()

Note the various configuration aspects like field length and the like
will automatically be mapped. This means that getting a ``Deform`` form
to use ``ColanderAlchemy`` is as simple as using any other ``Colander``
schema::

    from colanderalchemy import SQLAlchemySchemaNode
    from deform import Form

    # Using Colander requires manually constructing the schema
    # person = Person()

    # Using ColanderAlchemy is easy!
    person = SQLAlchemySchemaNode(Person)
    
    form = Form(person, buttons=('submit',))

Keep in mind that if you want additional control over the resulting
``Colander`` schema and nodes produced (such as controlling a node's `title`,
`description`, `widget` or more), you are able to provide appropriate keyword
arguments declaratively within the ``SQLAlchemy`` model as part of the
respective ``info`` argument to a :class:`sqlalchemy.Column` or
:meth:`sqlalchemy.orm.relationship` declaration. For more information, see
:ref:`customization`.
