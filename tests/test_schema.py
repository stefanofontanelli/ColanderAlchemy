# test_declarative.py
# Copyright (C) 2012 the ColanderAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of ColanderAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from colanderalchemy import (setup_schema,
                             SQLAlchemySchemaNode)
from sqlalchemy import (event,
                        inspect)
from sqlalchemy.orm import mapper
from .models import (Account,
                     Person,
                     Address)
import colander
import logging
import sys

if sys.version_info[0] == 2 and sys.version_info[1] < 7:
    # In Python < 2.7 use unittest2.
    import unittest2 as unittest

else:
    import unittest


log = logging.getLogger(__name__)


class TestsSQLAlchemySchemaNode(unittest.TestCase):

    def setUp(self):
        event.listen(mapper, 'mapper_configured', setup_schema)
        
    def tearDown(self):
        pass
    
    def test_setup_schema(self):
        for cls in [Account, Person, Address]:
            self.assertEqual(isinstance(cls.__colanderalchemy__,
                                        SQLAlchemySchemaNode),
                             True)

    def test_default_strategy_for_columns_and_relationships_include_all(self):
        account_schema = SQLAlchemySchemaNode(Account)
        m = inspect(Account)
        for attr in m.attrs:
            self.assertIn(attr.key, account_schema)

    def test_default_strategy_for_included_relationships_schema(self):
        account_schema = SQLAlchemySchemaNode(Account)
        m = inspect(Person)
        for attr in m.column_attrs:
            self.assertIn(attr.key, account_schema['person'])

        for attr in m.relationships:
            self.assertNotIn(attr.key, account_schema['person'])

    def test_imperative_includes(self):
        m = inspect(Account)
        includes = [attr.key for attr in m.column_attrs]
        account_schema = SQLAlchemySchemaNode(Account, includes=includes)
        for attr in m.column_attrs:
            self.assertIn(attr.key, account_schema)

        for attr in m.relationships:
            self.assertNotIn(attr.key, account_schema)

    def test_imperative_excludes(self):
        m = inspect(Account)
        excludes = [attr.key for attr in m.column_attrs]
        account_schema = SQLAlchemySchemaNode(Account, excludes=excludes)
        for attr in m.column_attrs:
            self.assertNotIn(attr.key, account_schema)

        for attr in m.relationships:
            self.assertIn(attr.key, account_schema)

    def test_imperative_colums_overrides(self):
        m = inspect(Account)
        overrides = {
            'email': {
                'typ': colander.Integer()
            }
        }
        account_schema = SQLAlchemySchemaNode(Account, overrides=overrides)
        self.assertNotEqual(isinstance(account_schema['email'].typ,
                                       colander.String),
                            True)
        self.assertEqual(isinstance(account_schema['email'].typ,
                                    colander.Integer),
                         True)

    def test_declarative_exclude(self):
        m = inspect(Address)
        address_schema = SQLAlchemySchemaNode(Address)
        self.assertNotIn('city', address_schema)
        self.assertNotIn('person', address_schema)
        for attr in m.attrs:
            if attr.key not in ('city', 'person'):
                self.assertIn(attr.key, address_schema)
