# models.py
# Copyright (C) 2012 the ColanderAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of ColanderAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import colander
import colanderalchemy
import datetime
import sqlalchemy
import sqlalchemy.ext.declarative
import sqlalchemy.orm
import sqlalchemy.schema
import sys


Base = sqlalchemy.ext.declarative.declarative_base()


class Account(Base):

    __tablename__ = 'accounts'

    email = sqlalchemy.Column(sqlalchemy.Unicode(256),
                              primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.Unicode(128),
                             nullable=False)
    surname = sqlalchemy.Column(sqlalchemy.Unicode(128),
                                nullable=False)
    gender = sqlalchemy.Column(sqlalchemy.Enum('M', 'F'),
                               nullable=False)
    contact = sqlalchemy.orm.relationship('Contact',
                                          uselist=False,
                                          back_populates='account')
    themes = sqlalchemy.orm.relationship('Theme',
                                         back_populates='author')


class Contact(Base):

    __tablename__ = 'contacts'

    type_ = sqlalchemy.Column(sqlalchemy.Unicode(256),
                              primary_key=True)
    value = sqlalchemy.Column(sqlalchemy.Unicode(256),
                              nullable=False)
    account_id = sqlalchemy.Column(sqlalchemy.Unicode(256),
                                   sqlalchemy.ForeignKey('accounts.email'),
                                   primary_key=True)
    account = sqlalchemy.orm.relationship('Account',
                                          back_populates='contact')


class Theme(Base):

    __tablename__ = 'themes'

    name = sqlalchemy.Column(sqlalchemy.Unicode(256),
                             primary_key=True)
    description = sqlalchemy.Column(sqlalchemy.UnicodeText,
                                    default='')
    author_id = sqlalchemy.Column(sqlalchemy.Unicode(256),
                                  sqlalchemy.ForeignKey('accounts.email'),
                                  primary_key=True)
    author = sqlalchemy.orm.relationship('Account',
                                         back_populates='themes')
    templates = sqlalchemy.orm.relationship('Template',
                                            back_populates='theme')


class Template(Base):

    __tablename__ = 'templates'

    __table_args__ = (
        sqlalchemy.schema.ForeignKeyConstraint(
            ['theme_name', 'theme_author_id'],
            ['themes.name', 'themes.author_id'],
            onupdate='CASCADE',
            ondelete='CASCADE'
        ),
    )

    name = sqlalchemy.Column(sqlalchemy.Unicode(128),
                             primary_key=True)
    theme_name = sqlalchemy.Column(sqlalchemy.Unicode(256),
                                   primary_key=True)
    theme_author_id = sqlalchemy.Column(sqlalchemy.Unicode(256),
                                        primary_key=True)
    theme = sqlalchemy.orm.relationship('Theme',
                                        back_populates='templates')


class Person(Base):

    __tablename__ = 'person'
    id = colanderalchemy.Column(sqlalchemy.Integer,
                                primary_key=True,
                                ca_type=colander.Float(),
                                ca_title='Person ID',
                                ca_description='The Person id.',
                                ca_widget='Empty Widget',
                                ca_include=True)
    name = colanderalchemy.Column(sqlalchemy.Unicode(128),
                                  nullable=False,
                                  ca_nullable=True,
                                  ca_include=True,
                                  ca_default=colander.required)
    surname = colanderalchemy.Column(sqlalchemy.Unicode(128),
                                     nullable=False,
                                     ca_exclude=True)
    addresses = colanderalchemy.relationship('Address',
                                             ca_exclude=True)


class Address(Base):

    __tablename__ = 'addresses'

    id = colanderalchemy.Column(sqlalchemy.Integer,
                                primary_key=True,
                                ca_missing=colander.null)
    street = colanderalchemy.Column(sqlalchemy.Unicode(128),
                                    nullable=False)
    city = colanderalchemy.Column(sqlalchemy.Unicode(128),
                                  nullable=False)
    person_id = colanderalchemy.Column(sqlalchemy.Unicode(128),
                                       sqlalchemy.ForeignKey('person.id'),
                                       primary_key=True)
    person = colanderalchemy.relationship('Person',
                                          ca_title='Person relationship.',
                                          ca_description='The Person desc.',
                                          ca_widget='Rel. Empty Widget')


class LogEntry(Base):

    __tablename__ = 'logentries'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True)
    created = sqlalchemy.Column(sqlalchemy.DateTime,
                                default=datetime.datetime.utcnow,
                                nullable=True)
    modified = sqlalchemy.Column(sqlalchemy.DateTime,
                                 default=lambda: datetime.datetime.utcnow() + \
                                                 datetime.timedelta(1),
                                 nullable=True)


class Timestamped(object):
    """ An automatically timestamped mixin. """
    ins_date = colanderalchemy.Column(sqlalchemy.DateTime,
                                      nullable=False,
                                      default=datetime.datetime.utcnow,
                                      ca_exclude=True)
    mod_date = colanderalchemy.Column(sqlalchemy.DateTime,
                                      ca_include=False,
                                      nullable=False,
                                      default=datetime.datetime.utcnow)


TimeBase = sqlalchemy.ext.declarative.declarative_base(cls=Timestamped)


class Versioned(TimeBase):

    __tablename__ = 'versions'
    id = colanderalchemy.Column(sqlalchemy.Integer, primary_key=True)
