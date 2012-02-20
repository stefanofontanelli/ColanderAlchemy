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


class Theme(Base):
    __tablename__ = 'themes'
    name = sqlalchemy.Column(sqlalchemy.Unicode(256), primary_key=True)
    description = sqlalchemy.Column(sqlalchemy.UnicodeText, default='')
    author_id = sqlalchemy.Column(sqlalchemy.Unicode(256),
                                  sqlalchemy.ForeignKey('accounts.email'),
                                  primary_key=True)
    author = sqlalchemy.orm.relationship('Account', backref='themes')


class Template(Base):
    __tablename__ = 'templates'
    __table_args__ = (
        sqlalchemy.schema.ForeignKeyConstraint(['theme_name',
                                                'theme_author_id'],
                                               ['themes.name',
                                                'themes.author_id'],
                                               onupdate='CASCADE',
                                               ondelete='CASCADE'),
    )
    name = sqlalchemy.Column(sqlalchemy.Unicode(128), primary_key=True)
    theme_name = sqlalchemy.Column(sqlalchemy.Unicode(256),
                                   primary_key=True)
    theme_author_id = sqlalchemy.Column(sqlalchemy.Unicode(256),
                                        primary_key=True)
    theme = sqlalchemy.orm.relationship('Theme')


class TestsBase(unittest.TestCase):

    def setUp(self):
        self.engine = sqlalchemy.create_engine('sqlite://')
        Base.metadata.bind = self.engine
        Base.metadata.create_all(self.engine)
        self.Session = sqlalchemy.orm.sessionmaker(bind=self.engine)
        self.session = self.Session()
        self.account = colanderalchemy.Schema(Account, self.session)
        self.theme = colanderalchemy.Schema(Theme, self.session)
        self.template = colanderalchemy.Schema(Template, self.session)

    def tearDown(self):
        self.session.rollback()
        self.session.close()

    def test_account(self):
        # Test for required fields (ex. primary keys).
        self.assertRaises(colander.Invalid,
                          self.account.deserialize,
                          {})
        # Test below fails due to nullable fields.
        self.assertRaises(colander.Invalid,
                          self.account.deserialize,
                          {'email': 'mailbox@domain.tld'})
        self.assertRaises(colander.Invalid,
                          self.account.deserialize,
                          {'email': 'mailbox@domain.tld',
                           'name': 'My Name.'})
        self.assertRaises(colander.Invalid,
                          self.account.deserialize,
                          {'email': 'mailbox@domain.tld',
                           'name': 'My Name.',
                           'surname': 'My Surname.'})
        self.assertRaises(colander.Invalid,
                          self.account.deserialize,
                          {'email': 'mailbox@domain.tld',
                           'name': 'My Name.',
                           'surname': 'My Surname.',
                           'gender': 'A'})

    def test_theme(self):

        self.assertRaises(colander.Invalid,
                          self.theme.deserialize,
                          {})
        self.assertRaises(colander.Invalid,
                          self.theme.deserialize,
                          {'name': 'My Name.'})
        self.assertRaises(colander.Invalid,
                          self.theme.deserialize,
                          {'author_id': 'mailbox@domain.tld'})
        self.assertRaises(colander.Invalid,
                          self.theme.deserialize,
                          {'name': 'My Name.',
                           'author_id': 'mailbox@domain.tld',
                           'author': None})
        self.assertRaises(colander.Invalid,
                          self.theme.deserialize,
                          {'name': 'My Name.',
                           'author_id': 'mailbox@domain.tld',
                           'author': {}})

    def test_template(self):

        self.assertRaises(colander.Invalid,
                  self.template.deserialize,
                  {})
        self.assertRaises(colander.Invalid,
                          self.template.deserialize,
                          {'name': 'My Name.'})
        self.assertRaises(colander.Invalid,
                          self.template.deserialize,
                          {'theme_name': 'Its Name.'})
        self.assertRaises(colander.Invalid,
                          self.template.deserialize,
                          {'theme_author_id': 'mailbox@domain.tld'})
        self.assertRaises(colander.Invalid,
                          self.template.deserialize,
                          {'name': 'My Name.',
                           'theme_name': 'Its Name.',
                           'theme_author_id': 'mailbox@domain.tld',
                           'theme': {}})
        self.assertRaises(colander.Invalid,
                          self.template.deserialize,
                          {'name': 'My Name.',
                           'theme_name': 'Its Name.',
                           'theme_author_id': 'mailbox@domain.tld',
                           'theme': None})
        self.assertRaises(colander.Invalid,
                          self.template.deserialize,
                          {'name': 'My Name.',
                           'theme_name': 'Theme Name.',
                           'theme_author_id': 'mailbox@domain.tld',
                           'theme': {
                               'name': 'Theme Name.',
                               'author_id': 'mailbox@domain.tld',
                           }})

    def test_deserialize(self):
        a1 = {
            'email': 'mailbox_1@domain.tld',
            'name': 'My Name.',
            'surname': 'My Surname.',
            'gender': 'M',
        }
        a1 = self.account.deserialize(a1)
        self.session.add(a1)
        a2 = {
            'email': 'mailbox_2@domain.tld',
            'name': 'My Name.',
            'surname': 'My Surname.',
            'gender': 'F',
        }
        a2 = self.account.deserialize(a2)
        self.session.add(a2)

        theme1 = {
            'name': 'Theme Name.',
            'author_id': 'mailbox_1@domain.tld',
            'description': 'Template Description.',
        }
        theme1 = self.theme.deserialize(theme1)
        self.session.add(theme1)

        t1 = {
            'name': 'My Name.',
            'theme_name': 'Theme Name.',
            'theme_author_id': 'mailbox_1@domain.tld',
        }
        t1 = self.template.deserialize(t1)
        self.session.add(t1)
        self.assertEqual(t1.theme, theme1)
        t2 = {
            'name': 'My Name.',
            'theme_name': 'Theme Name.',
            'theme_author_id': 'mailbox_1@domain.tld',
            'theme': {
                'name': 'Theme Name.',
                'author_id': 'mailbox_1@domain.tld',
            },
        }
        t2 = self.template.deserialize(t2)
        self.session.add(t2)
        self.assertEqual(t2.theme, theme1)
