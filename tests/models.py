# models.py
# Copyright (C) 2012 the ColanderAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of ColanderAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import colander
from colanderalchemy import SQLAlchemySchemaNode
from sqlalchemy import (Boolean,
                        Column,
                        Date,
                        DateTime,
                        Enum,
                        Float,
                        ForeignKey,
                        Integer,
                        Numeric,
                        Time,
                        Unicode)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime


Base = declarative_base()
key = SQLAlchemySchemaNode.sqla_info_key


class Account(Base):

    __tablename__ = 'accounts'
    __colanderalchemy_config__ = {'preparer': 'DummyPreparer'}
    email = Column(Unicode(64), primary_key=True)
    enabled = Column(Boolean, default=True)
    created = Column(DateTime, nullable=True, default=datetime.datetime.now)
    timeout = Column(Time, nullable=False)
    person_id = Column(Integer, ForeignKey('people.id'))
    person = relationship('Person')


class Person(Base):

    __tablename__ = 'people'
    __colanderalchemy_config__ = {'widget': 'DummyWidget',
                                  'title': 'Person Object'}

    id = Column(Integer, primary_key=True, info={key: {'typ': colander.Float}})
    name = Column(Unicode(32), nullable=False)
    surname = Column(Unicode(32), nullable=False)
    gender = Column(Enum('M', 'F'), nullable=False)
    birthday = Column(Date, nullable=True)
    age = Column(Integer, nullable=True)
    addresses = relationship('Address',
                             info={
                                key: {
                                    'overrides': {
                                        'id': {
                                            'typ': colander.Float
                                        }
                                    }
                                }
                             })


class Address(Base):

    __tablename__ = 'addresses'

    id = Column(Integer, primary_key=True)
    street = Column(Unicode(64), nullable=False)
    city = Column(Unicode(32), nullable=False, info={key: {'exclude': True}})
    latitude = Column(Float, nullable=True)
    longitude = Column(Numeric, nullable=True)
    person_id = Column(Integer, ForeignKey('people.id'))
    person = relationship(Person, info={key: {'exclude': True}})
