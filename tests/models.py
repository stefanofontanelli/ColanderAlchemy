# models.py
# Copyright (C) 2012 the ColanderAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of ColanderAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import datetime

import colander
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    Time,
    Unicode,
    event
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (relationship, mapper)

from colanderalchemy import (SQLAlchemySchemaNode, setup_schema)


Base = declarative_base()
key = SQLAlchemySchemaNode.sqla_info_key

event.listen(mapper, 'mapper_configured', setup_schema)


def has_unique_addresses(node, value):
    """ Dummy validator for schema. """
    pass


class Account(Base):

    __tablename__ = 'accounts'
    __colanderalchemy_config__ = {'preparer': 'DummyPreparer',
                                  'unknown': 'raise'}
    email = Column(Unicode(64), primary_key=True)
    enabled = Column(Boolean, default=True)
    created = Column(DateTime, nullable=True,
                     default=datetime.datetime.now)
    timeout = Column(Time, nullable=False)
    person_id = Column(Integer, ForeignKey('people.id'))
    person = relationship('Person')


class Person(Base):

    __tablename__ = 'people'
    __colanderalchemy_config__ = {'widget': 'DummyWidget',
                                  'title': 'Person Object'}

    id = Column(Integer, primary_key=True,
                info={key: {'typ': colander.Float}})
    name = Column(Unicode(32), nullable=False)
    surname = Column(Unicode(32), nullable=False)
    gender = Column(Enum('M', 'F'), nullable=False)
    birthday = Column(Date, nullable=True)
    age = Column(Integer, nullable=True)
    addresses = relationship(
        'Address',
        info={
            key: {
                'title': 'Your addresses',
                'validator': has_unique_addresses,
                'overrides': {
                    'id': {
                        'typ': colander.Float
                    }
                }
            }
        }
    )


class Group(Base):

    __tablename__ = 'groups'

    identifier = Column(Unicode, primary_key=True)
    leader = relationship('Person',
                          uselist=False,
                          innerjoin=True,
                          secondary='group_associations')
    executive = relationship('Person',
                             uselist=True,
                             innerjoin=True,
                             secondary='group_associations')
    members = relationship('Person',
                           uselist=True,
                           secondary='group_associations')


class GroupAssociations(Base):

    __tablename__ = 'group_associations'

    group_id = Column(Unicode, ForeignKey(Group.identifier),
                      primary_key=True)
    person_id = Column(Integer, ForeignKey(Person.id), primary_key=True)


class Address(Base):

    __tablename__ = 'addresses'
    __colanderalchemy_config__ = {
        'title': 'address',
        'description': 'A location associated with a person.',
        'widget': 'dummy'
    }

    id = Column(Integer, primary_key=True)
    street = Column(Unicode(64), nullable=False)
    city = Column(Unicode(32), nullable=False,
                  info={key: {'exclude': True}})
    latitude = Column(Float, nullable=True)
    longitude = Column(Numeric, nullable=True)
    person_id = Column(Integer, ForeignKey('people.id'))
    person = relationship(Person, info={key: {'exclude': True}})
