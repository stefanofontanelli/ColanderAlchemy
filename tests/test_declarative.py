# test_declarative.py
# Copyright (C) 2012 the ColanderAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of ColanderAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from models import Address
from models import Person
from models import Versioned
import colander
import colanderalchemy
import logging
import sys

if sys.version_info[0] == 2 and sys.version_info[1] < 7:
    # In Python < 2.7 use unittest2.
    import unittest2 as unittest

else:
    import unittest


log = logging.getLogger(__name__)


class TestsBase(unittest.TestCase):

    def setUp(self):
        self.address = colanderalchemy.SQLAlchemyMapping(Address)
        self.person = colanderalchemy.SQLAlchemyMapping(Person)
        self.versioned = colanderalchemy.SQLAlchemyMapping(Versioned)

    def tearDown(self):
        pass

    def test_column(self):
        self.assertEqual(type(self.person['id'].typ), colander.Float)
        self.assertEqual(self.person['id'].title, 'Person ID')
        self.assertEqual(self.person['id'].description, 'The Person id.')
        self.assertEqual(self.person['id'].widget, 'Empty Widget')
        self.assertRaises(KeyError, self.person.__getitem__, 'surname')
        self.assertEqual(self.person['name'].default, colander.required)
        self.assertEqual(self.address['id'].missing, colander.null)

    def test_relationship(self):
        self.assertRaises(KeyError, self.person.__getitem__, 'addresses')
        self.assertEqual(self.address['person'].title, 'Person relationship.')
        self.assertEqual(self.address['person'].description, 'The Person desc.')
        self.assertEqual(self.address['person'].widget, 'Rel. Empty Widget')

    def test_column_inheritance(self):
        self.assertRaises(colander.Invalid,
                          self.versioned.deserialize,
                          {})
        self.assertRaises(colander.Invalid,
                          self.versioned.deserialize,
                          {'id': '1'})
