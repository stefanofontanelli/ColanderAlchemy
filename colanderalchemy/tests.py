#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
        self.account = colanderalchemy.Schema(Account, self.session)
        self.contact = colanderalchemy.Schema(Contact, self.session)
        self.theme = colanderalchemy.Schema(Theme, self.session)
        self.template = colanderalchemy.Schema(Template, self.session)

    def tearDown(self):
        self.session.rollback()
        self.session.close()

    def setUp(self):
        self.engine = sqlalchemy.create_engine('sqlite://')
        Base.metadata.bind = self.engine
        Base.metadata.create_all(self.engine)
        self.Session = sqlalchemy.orm.sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.account = colanderalchemy.Schema(Account, self.session)
        self.contact = colanderalchemy.Schema(Contact, self.session)
        self.theme = colanderalchemy.Schema(Theme, self.session)
        self.template = colanderalchemy.Schema(Template, self.session)

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
        self.assertIn('email', self.account.registry.keys)
        self.assertIn('email', self.account.registry.fields)
        self.assertIn('name', self.account.registry.fields)
        self.assertIn('surname', self.account.registry.fields)
        self.assertIn('gender', self.account.registry.fields)
        self.assertIn('themes', self.account.registry.relationships)
        self.assertIn('themes', self.account.registry.rkeys)
        self.assertIn('contact', self.account.registry.references)
        self.assertEqual(self.account.registry.fkeys, {})
        self.assertIn('themes', self.account.registry.collections)

    def test_contact_registry(self):
        self.assertIn('type_', self.contact.registry.keys)
        self.assertIn('account_id', self.contact.registry.keys)
        self.assertIn('type_', self.contact.registry.fields)
        self.assertIn('value', self.contact.registry.fields)
        self.assertIn('account_id', self.contact.registry.fields)
        self.assertIn('account', self.contact.registry.relationships)
        self.assertIn('account', self.contact.registry.rkeys)
        self.assertIn('account', self.contact.registry.references)
        self.assertIn('account', self.contact.registry.fkeys)
        self.assertEqual(self.contact.registry.collections, set())

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
        self.assertIn('name', self.theme.registry.keys)
        self.assertIn('author_id', self.theme.registry.keys)
        self.assertIn('name', self.theme.registry.fields)
        self.assertIn('description', self.theme.registry.fields)
        self.assertIn('author_id', self.theme.registry.fields)
        self.assertIn('author', self.theme.registry.relationships)
        self.assertIn('author', self.theme.registry.rkeys)
        self.assertIn('author', self.theme.registry.references)
        self.assertIn('author', self.theme.registry.fkeys)
        self.assertIn('templates', self.theme.registry.collections)

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
        self.assertRaises(colander.Invalid, self.template.deserialize,
                          {'name': 'My Name.',
                           'theme_name': 'Theme Name.',
                           'theme_author_id': 'mailbox@domain.tld',
                           'theme': {'name': 'Theme Name.',
                                     'author_id': 'mailbox@domain.tld'}
                           })

    def test_template_registry(self):
        self.assertIn('name', self.template.registry.keys)
        self.assertIn('theme_name', self.template.registry.keys)
        self.assertIn('theme_author_id', self.template.registry.keys)
        self.assertIn('name', self.template.registry.fields)
        self.assertIn('theme_name', self.template.registry.fields)
        self.assertIn('theme_author_id', self.template.registry.fields)
        self.assertIn('theme', self.template.registry.relationships)
        self.assertIn('theme', self.template.registry.rkeys)
        self.assertIn('theme', self.template.registry.references)
        self.assertIn('theme', self.template.registry.fkeys)
        self.assertEqual(self.template.registry.collections, set())

    def test_deserialize_serialize(self):
        a1 = {
            'email': 'mailbox_1@domain.tld',
            'name': 'My Name.',
            'surname': 'My Surname.',
            'gender': 'M'
        }
        a1 = self.account.deserialize(a1)
        self.session.add(a1)
        a2 = {
            'email': 'mailbox_2@domain.tld',
            'name': 'My Name.',
            'surname': 'My Surname.',
            'gender': 'F'
        }
        a2 = self.account.deserialize(a2)
        self.session.add(a2)

        theme1 = {
            'name': 'Theme Name.',
            'author_id': 'mailbox_1@domain.tld',
            'description': 'Template Description.'
        }
        theme1 = self.theme.deserialize(theme1)
        self.session.add(theme1)
        self.assertEqual(theme1.author, a1)
        self.assertIn(theme1, a1.themes)

        t1 = {
            'name': 'My Name.',
            'theme_name': 'Theme Name.',
            'theme_author_id': 'mailbox_1@domain.tld'
        }
        t1 = self.template.deserialize(t1)
        self.session.add(t1)
        self.assertEqual(t1.theme, theme1)
        self.assertIn(t1, theme1.templates)

        t2 = {
            'name': 'My Name.',
            'theme_name': 'Theme Name.',
            'theme_author_id': 'mailbox_1@domain.tld',
            'theme': {
            'name': 'Theme Name.',
            'author_id': 'mailbox_1@domain.tld'
        },
        }
        t2 = self.template.deserialize(t2)
        self.session.add(t2)
        self.assertEqual(t2.theme, theme1)
        self.assertIn(t2, theme1.templates)

        a1_colander = self.account.serialize(a1, True)
        a1_dict = self.account.serialize(a1, False)
        self.assertEqual(a1_colander.keys(), a1_dict.keys())
        self.assertIn('email', a1_colander)
        self.assertIn('name', a1_colander)
        self.assertIn('surname', a1_colander)
        self.assertIn('gender', a1_colander)
        self.assertIn('contact', a1_colander)
        self.assertIn('themes', a1_colander)
        self.assertEqual(a1_dict['contact'], None)
        self.assertIn('type_', a1_colander['contact'])
        self.assertIn('account_id', a1_colander['contact'])
        self.assertNotEqual(a1_colander['themes'], [])
        self.assertNotEqual(a1_dict['themes'], [])

    def test_excludes(self):
        excludes = ('email', 'name', 'surname', 'gender', 'contact', 'themes')
        account = colanderalchemy.Schema(Account,
                                         self.session,
                                         excludes=excludes)
        self.assertEqual(isinstance(account.deserialize({}), Account), True)
        self.assertEqual(account.serialize(account.deserialize({})), {})
        self.assertEqual(account.serialize(account.deserialize({}),
                                           use_colander=False),
                         {
                            'email': None,
                            'name': None,
                            'surname': None,
                            'gender': None,
                            'contact': None,
                            'themes': []
                         })
        account = colanderalchemy.Schema(Account,
                                         self.session,
                                         excludes=excludes)
        self.assertEqual(account.deserialize({}, colander_only=True), {})

    def test_nullables(self):
        nullables = {
            'email': True,
            'name': True,
            'surname': True,
            'gender': True,
            'contact': True,
            'themes': True
        }
        account = colanderalchemy.Schema(Account,
                                         self.session,
                                         nullables=nullables)
        self.assertEqual(isinstance(account.deserialize({}), Account), True)
        account = colanderalchemy.Schema(Account,
                                         self.session,
                                         nullables=nullables)
        self.assertEqual(account.deserialize({}, colander_only=True),
                         {
                            'email': None,
                            'name': None,
                            'surname': None,
                            'gender': None,
                            'contact': None,
                            'themes': []
                         })
