# tests.py
# Copyright (C) 2012 the ColanderAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of ColanderAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php


import colander
import colanderalchemy
import logging
import sqlalchemy
import sqlalchemy.ext.declarative
import sqlalchemy.orm
import sqlalchemy.schema
import unittest


log = logging.getLogger(__name__)
Base = sqlalchemy.ext.declarative.declarative_base()


class Account(Base):
    __tablename__ = 'accounts'
    email = sqlalchemy.Column(sqlalchemy.Unicode(256), primary_key=True)
    name = sqlalchemy.Column(sqlalchemy.Unicode(128), nullable=False)
    surname = sqlalchemy.Column(sqlalchemy.Unicode(128), nullable=False)
    gender = sqlalchemy.Column(sqlalchemy.Enum(u'M', u'F'), nullable=False)
    contact = sqlalchemy.orm.relationship('Contact', uselist=False,
    back_populates='account')
    themes = sqlalchemy.orm.relationship('Theme', back_populates='author')


class Contact(Base):
    __tablename__ = 'contacts'
    type_ = sqlalchemy.Column(sqlalchemy.Unicode(256), primary_key=True)
    value = sqlalchemy.Column(sqlalchemy.Unicode(256), nullable=False)
    account_id = sqlalchemy.Column(sqlalchemy.Unicode(256),
    sqlalchemy.ForeignKey('accounts.email'),
    primary_key=True)
    account = sqlalchemy.orm.relationship('Account', back_populates='contact')


class Theme(Base):
    __tablename__ = 'themes'
    name = sqlalchemy.Column(sqlalchemy.Unicode(256), primary_key=True)
    description = sqlalchemy.Column(sqlalchemy.UnicodeText, default='')
    author_id = sqlalchemy.Column(sqlalchemy.Unicode(256),
    sqlalchemy.ForeignKey('accounts.email'),
    primary_key=True)
    author = sqlalchemy.orm.relationship('Account', back_populates='themes')
    templates = sqlalchemy.orm.relationship('Template', back_populates='theme')


class Template(Base):
    __tablename__ = 'templates'
    __table_args__ = (
        sqlalchemy.schema.ForeignKeyConstraint(
            ['theme_name', 'theme_author_id'],
            ['themes.name', 'themes.author_id'],
            onupdate='CASCADE', ondelete='CASCADE'),
    )
    name = sqlalchemy.Column(sqlalchemy.Unicode(128), primary_key=True)
    theme_name = sqlalchemy.Column(sqlalchemy.Unicode(256), primary_key=True)
    theme_author_id = sqlalchemy.Column(sqlalchemy.Unicode(256),
                                        primary_key=True)
    theme = sqlalchemy.orm.relationship('Theme', back_populates='templates')


class TestsBase(unittest.TestCase):

    def setUp(self):
        self.engine = sqlalchemy.create_engine('sqlite://')
        Base.metadata.bind = self.engine
        Base.metadata.create_all(self.engine)
        self.Session = sqlalchemy.orm.sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.account = colanderalchemy.SQLAlchemyMapping(Account)
        self.contact = colanderalchemy.SQLAlchemyMapping(Contact)
        self.theme = colanderalchemy.SQLAlchemyMapping(Theme)
        self.template = colanderalchemy.SQLAlchemyMapping(Template)

    def tearDown(self):
        self.session.rollback()
        self.session.close()

    def test_account(self):
        # Test for required fields (ex. primary keys).
        self.assertRaises(colander.Invalid, self.account.deserialize, {})
        # Test below fails due to nullable fields.
        self.assertRaises(colander.Invalid, self.account.deserialize,
                          {'email': 'mailbox@domain.tld'})
        self.assertRaises(colander.Invalid, self.account.deserialize,
                          {'email': 'mailbox@domain.tld',
                           'name': 'My Name.'})
        self.assertRaises(colander.Invalid, self.account.deserialize,
                          {'email': 'mailbox@domain.tld',
                           'name': 'My Name.',
                           'surname': 'My Surname.'})
        self.assertRaises(colander.Invalid, self.account.deserialize,
                          {'email': 'mailbox@domain.tld',
                           'name': 'My Name.',
                           'surname': 'My Surname.',
                           'gender': 'A'})

    def test_account_registry(self):
        self.assertIn('email', self.account._reg.pkeys)
        self.assertIn('email', self.account._reg.fields)
        self.assertIn('name', self.account._reg.fields)
        self.assertIn('surname', self.account._reg.fields)
        self.assertIn('gender', self.account._reg.fields)
        self.assertIn('themes', self.account._reg.relationships)
        self.assertIn('themes', self.account._reg.rkeys)
        self.assertIn('contact', self.account._reg.references)
        self.assertEqual(self.account._reg.fkeys, {})
        self.assertIn('themes', self.account._reg.collections)

    def test_contact_registry(self):
        self.assertIn('type_', self.contact._reg.pkeys)
        self.assertIn('account_id', self.contact._reg.pkeys)
        self.assertIn('type_', self.contact._reg.fields)
        self.assertIn('value', self.contact._reg.fields)
        self.assertIn('account_id', self.contact._reg.fields)
        self.assertIn('account', self.contact._reg.relationships)
        self.assertIn('account', self.contact._reg.rkeys)
        self.assertIn('account', self.contact._reg.references)
        self.assertIn('account', self.contact._reg.fkeys)
        self.assertEqual(self.contact._reg.collections, set())

    def test_theme(self):
        self.assertRaises(colander.Invalid, self.theme.deserialize, {})
        self.assertRaises(colander.Invalid, self.theme.deserialize,
                          {'name': 'My Name.'})
        self.assertRaises(colander.Invalid, self.theme.deserialize,
                          {'author_id': 'mailbox@domain.tld'})
        self.assertRaises(colander.Invalid, self.theme.deserialize,
                          {'name': 'My Name.',
                           'author_id': 'mailbox@domain.tld',
                           'author': None})
        self.assertRaises(colander.Invalid, self.theme.deserialize,
                          {'name': 'My Name.',
                           'author_id': 'mailbox@domain.tld',
                           'author': {}})

    def test_theme_registry(self):
        self.assertIn('name', self.theme._reg.pkeys)
        self.assertIn('author_id', self.theme._reg.pkeys)
        self.assertIn('name', self.theme._reg.fields)
        self.assertIn('description', self.theme._reg.fields)
        self.assertIn('author_id', self.theme._reg.fields)
        self.assertIn('author', self.theme._reg.relationships)
        self.assertIn('author', self.theme._reg.rkeys)
        self.assertIn('author', self.theme._reg.references)
        self.assertIn('author', self.theme._reg.fkeys)
        self.assertIn('templates', self.theme._reg.collections)

    def test_template(self):
        self.assertRaises(colander.Invalid, self.template.deserialize, {})
        self.assertRaises(colander.Invalid, self.template.deserialize,
                          {'name': 'My Name.'})
        self.assertRaises(colander.Invalid, self.template.deserialize,
                          {'theme_name': 'Its Name.'})
        self.assertRaises(colander.Invalid, self.template.deserialize,
                          {'theme_author_id': 'mailbox@domain.tld'})
        self.assertRaises(colander.Invalid, self.template.deserialize,
                          {'name': 'My Name.',
                           'theme_name': 'Its Name.',
                           'theme_author_id': 'mailbox@domain.tld',
                           'theme': {}})
        self.assertRaises(colander.Invalid, self.template.deserialize,
                          {'name': 'My Name.',
                           'theme_name': 'Its Name.',
                           'theme_author_id': 'mailbox@domain.tld',
                           'theme': None})

    def test_template_registry(self):
        self.assertIn('name', self.template._reg.pkeys)
        self.assertIn('theme_name', self.template._reg.pkeys)
        self.assertIn('theme_author_id', self.template._reg.pkeys)
        self.assertIn('name', self.template._reg.fields)
        self.assertIn('theme_name', self.template._reg.fields)
        self.assertIn('theme_author_id', self.template._reg.fields)
        self.assertIn('theme', self.template._reg.relationships)
        self.assertIn('theme', self.template._reg.rkeys)
        self.assertIn('theme', self.template._reg.references)
        self.assertIn('theme', self.template._reg.fkeys)
        self.assertEqual(self.template._reg.collections, set())

    def test_excludes(self):
        excludes = ('email', 'name', 'surname', 'gender', 'contact', 'themes')
        account = colanderalchemy.SQLAlchemyMapping(Account, excludes=excludes)
        data = account.deserialize({})
        self.assertEqual(data, {})
        self.assertEqual(account.serialize(data), {})

    def test_nullables(self):
        nullables = {
            'email': True,
            'name': True,
            'surname': True,
            'gender': True,
            'contact': True,
            'themes': True
        }
        account = colanderalchemy.SQLAlchemyMapping(Account,
                                                    nullables=nullables)
        data = {
            'contact': None,
            'email': None,
            'gender': None,
            'name': None,
            'surname': None,
            'themes': []
        }
        self.assertEqual(data, account.deserialize({}))
        data.pop('contact')
        self.assertEqual(account.serialize(data), {
            'contact': {'account_id': colander.null, 'type_': colander.null},
            'email': u'None',
            'gender': u'None',
            'name': u'None',
            'surname': u'None',
            'themes': []
        })
