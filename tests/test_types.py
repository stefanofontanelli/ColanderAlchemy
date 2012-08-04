# test_declarative.py
# Copyright (C) 2012 the ColanderAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of ColanderAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from models import Account
from models import Address
from models import Contact
from models import LogEntry
from models import Person
from models import Template
from models import Theme
import colander
import colanderalchemy
import datetime
import logging
import sys

if sys.version_info[0] == 2 and sys.version_info[1] < 7:
    # In Python < 2.7 use unittest2.
    import unittest2 as unittest

else:
    import unittest


log = logging.getLogger(__name__)


class TestsSQLAlchemyMapping(unittest.TestCase):

    def setUp(self):
        self.account = colanderalchemy.SQLAlchemyMapping(Account)
        self.address = colanderalchemy.SQLAlchemyMapping(Address)
        self.contact = colanderalchemy.SQLAlchemyMapping(Contact)
        self.logentry = colanderalchemy.SQLAlchemyMapping(LogEntry)
        self.person = colanderalchemy.SQLAlchemyMapping(Person)
        self.template = colanderalchemy.SQLAlchemyMapping(Template)
        self.theme = colanderalchemy.SQLAlchemyMapping(Theme)

    def tearDown(self):
        pass

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

    def test_relationship(self):
        self.assertEqual(self.account['contact'].title, "Contact")
        self.assertEqual(self.account['contact'].name, "contact")

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
        excludes = {
            'email': True,
            'name': True,
            'surname': True,
            'gender': True,
            'contact': True,
            'themes': True
        }
        account = colanderalchemy.SQLAlchemyMapping(Account, excludes=excludes)
        data = account.deserialize({})
        self.assertEqual(data, {})
        self.assertEqual(account.serialize(data), {})

    def test_includes(self):
        includes = {'email': True}
        account = colanderalchemy.SQLAlchemyMapping(Account, includes=includes)
        self.assertEqual(list(account.serialize({}).keys()), ['email'])

        self.assertRaises(ValueError, colanderalchemy.SQLAlchemyMapping,
                          Account, {'email': True}, {'email': True})
        self.assertRaises(ValueError, colanderalchemy.SQLAlchemyMapping,
                          Account, {'email': False}, {'email': False})

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
        self.assertEqual(account.serialize({}), {
            'contact': {'account_id': colander.null, 'type_': colander.null},
            'email': colander.null,
            'gender': colander.null,
            'name': colander.null,
            'surname': colander.null,
            'themes': colander.null
        })

    def test_clone(self):
        account = colanderalchemy.SQLAlchemyMapping(Account)
        account2 = account.clone()
        self.assertEqual(account._reg, account2._reg)
        self.assertEqual(len(account.children), len(account2.children))

    def test_dictify(self):
        params = {'email': 'mailbox@domain.tld',
                  'name': 'My Name.',
                  'surname': 'My Surname.',
                  'gender': 'M'}
        account = Account(**self.account.deserialize(params))
        dictified = self.account.dictify(account)
        params = {'email': 'mailbox@domain.tld',
                  'name': 'My Name.',
                  'surname': 'My Surname.',
                  'gender': 'M',
                  'contact': None,
                  'themes': []}
        self.assertEqual(dictified, params)

    def test_datetime(self):
        params = self.logentry.deserialize({'id': 1})
        self.assertIn('created', params)
        self.assertIn('modified', params)
        self.assertEqual(isinstance(params['created'], datetime.datetime),
                         True)
        self.assertEqual(isinstance(params['modified'], datetime.datetime),
                         True)
