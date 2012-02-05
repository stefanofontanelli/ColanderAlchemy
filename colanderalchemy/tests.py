#!/usr/bin/env python
# -*- coding: utf-8 -*-

import colander
import colanderalchemy
import sqlalchemy
#from sqlalchemy.orm import backref
#from sqlalchemy.orm import relationship
import sqlalchemy.ext.declarative
import unittest


class TestsBase(unittest.TestCase):

    def setUp(self):

        Base = sqlalchemy.ext.declarative.declarative_base()

        class StringColumn(Base):
            __tablename__ = 'string_column'
            id = sqlalchemy.Column(sqlalchemy.Integer,
                                   primary_key=True)
            name = sqlalchemy.Column(sqlalchemy.Unicode(8))

        class StringColumnNotNullable(Base):
            __tablename__ = 'string_column_not_nullable'
            id = sqlalchemy.Column(sqlalchemy.Integer,
                                   primary_key=True)
            name = sqlalchemy.Column(sqlalchemy.Unicode(8),
                                     nullable=False)

        class StringColumnWithDefault(Base):
            __tablename__ = 'string_column_with_default'
            id = sqlalchemy.Column(sqlalchemy.Integer,
                                   primary_key=True)
            name = sqlalchemy.Column(sqlalchemy.Unicode(8),
                                     default=u'Default Value')

        class StringColumnAsPK(Base):
            __tablename__ = 'string_column_as_pk'
            name = sqlalchemy.Column(sqlalchemy.Unicode(8),
                                     primary_key=True)

        class EnumColumn(StringColumnWithDefault):
            choice = sqlalchemy.Column(sqlalchemy.Enum(u'A', u'B'))

        self.StringColumn = StringColumn
        self.StringColumnNotNullable = StringColumnNotNullable
        self.StringColumnWithDefault = StringColumnWithDefault
        self.StringColumnAsPK = StringColumnAsPK
        self.EnumColumn = EnumColumn

    def test_string_column(self):
        schema = colanderalchemy.get_schema(self.StringColumn)

        self.assertRaises(colander.Invalid,
                          schema.deserialize, {})
        self.assertRaises(colander.Invalid,
                          schema.deserialize, {'name': 'A Name.'})

        self.assertEqual({'id': 1, 'name': None},
                         schema.deserialize({'id': 1}))

        registry = colanderalchemy.get_registry(schema)
        self.assertTrue('id' in registry)
        self.assertEqual(registry['id'], 'id')
        self.assertTrue('fields' in registry)
        self.assertEqual(registry['fields'], ['id', 'name'])

    def test_string_column_not_nullable(self):

        schema = colanderalchemy.get_schema(self.StringColumnNotNullable)

        self.assertRaises(colander.Invalid,
                          schema.deserialize, {'id': 1})
        self.assertRaises(colander.Invalid,
                          schema.deserialize, {'id': 1, 'name': None})

        self.assertEqual({'id': 1, 'name': 'My Name.'},
                         schema.deserialize({'id': 1, 'name': 'My Name.'}))

    def test_string_column_with_default(self):

        schema = colanderalchemy.get_schema(self.StringColumnWithDefault)
        self.assertEqual({'id': 1, 'name': 'Default Value'},
                         schema.deserialize({'id': 1}))

    def test_string_column_as_pk(self):

        schema = colanderalchemy.get_schema(self.StringColumnAsPK)
        self.assertRaises(colander.Invalid,
                          schema.deserialize, {})
        self.assertEqual({'name': 'My Name.'},
                         schema.deserialize({'name': 'My Name.'}))

    def test_enum_column(self):

        schema = colanderalchemy.get_schema(self.EnumColumn)
        self.assertRaises(colander.Invalid,
                          schema.deserialize, {'id': 1, 'choice': 'C'})
        data = {'id': 1, 'name': 'Default Value', 'choice': None}
        self.assertEqual(data, schema.deserialize({'id': 1}))
        data = {'id': 1, 'name': 'My Name.', 'choice': 'A'}
        self.assertEqual(data, schema.deserialize(data))
        data = {'id': 1, 'name': 'My Name.', 'choice': 'B'}
        self.assertEqual(data, schema.deserialize(data))
