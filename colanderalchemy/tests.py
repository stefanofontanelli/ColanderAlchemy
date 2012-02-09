#!/usr/bin/env python
# -*- coding: utf-8 -*-

import colander
import colanderalchemy
import sqlalchemy
#from sqlalchemy.orm import backref
import sqlalchemy.ext.declarative
import sqlalchemy.orm
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
            string_column_id = sqlalchemy.Column(sqlalchemy.Integer,
                                                 sqlalchemy.ForeignKey('string_column.id'))
            string_column = sqlalchemy.orm.relationship('StringColumn',
                                                        backref=sqlalchemy.orm.backref('pk_column',
                                                                                       uselist=False))

        class EnumColumn(StringColumnWithDefault):
            choice = sqlalchemy.Column(sqlalchemy.Enum(u'A', u'B'))
            string_column_id = sqlalchemy.Column(sqlalchemy.Integer,
                                                 sqlalchemy.ForeignKey('string_column.id'))
            string_column = sqlalchemy.orm.relationship('StringColumn', backref='enum_columns')

        self.engine = sqlalchemy.create_engine('sqlite://')
        Base.metadata.bind = self.engine
        Base.metadata.create_all(self.engine)
        self.Session = sqlalchemy.orm.sessionmaker(bind=self.engine)
        self.session = self.Session()

        self.StringColumn = StringColumn
        self.StringColumnNotNullable = StringColumnNotNullable
        self.StringColumnWithDefault = StringColumnWithDefault
        self.StringColumnAsPK = StringColumnAsPK
        self.EnumColumn = EnumColumn

        def tearDown(self):
            self.session.close()
            self.Session.close()
            self.engine.close()

    def test_string_column(self):
        schema = colanderalchemy.get_schema(self.StringColumn)

        self.assertRaises(colander.Invalid,
                          schema.deserialize, {})
        self.assertRaises(colander.Invalid,
                          schema.deserialize, {'name': 'A Name.'})
        self.assertRaises(colander.Invalid,
                          schema.deserialize, {'id': 'A Name.'})

        self.assertEqual({'id': 1, 'name': None, 'enum_columns': [], 'pk_column': None},
                         schema.deserialize({'id': 1}))

        registry = colanderalchemy.get_registry(schema)
        self.assertEqual(registry.id, 'id')
        self.assertEqual(registry.fields, ['id', 'name'])
        self.assertIn('enum_columns', registry.relationships.keys())
        self.assertIn('enum_columns', registry.collections.keys())
        self.assertIn('pk_column', registry.relationships.keys())
        self.assertIn('pk_column', registry.references.keys())

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
        self.assertEqual({'name': 'My Name.', 'string_column_id': None, 'string_column': None},
                         schema.deserialize({'name': 'My Name.'}))

    def test_enum_column(self):

        schema = colanderalchemy.get_schema(self.EnumColumn)
        self.assertRaises(colander.Invalid,
                          schema.deserialize, {'id': 1, 'choice': 'C'})
        data = {
          'id': 1,
          'name': 'Default Value',
          'choice': None,
          'string_column_id': None,
          'string_column': None,
        }
        self.assertRaises(colander.Invalid,
                          schema.deserialize, data)
        data = {
          'id': 1,
          'name': 'Default Value',
          'choice': None,
          'string_column_id': None,
          'string_column': None,
        }
        self.assertEqual(data, schema.deserialize({'id': 1}))
        data = {
          'id': 1,
          'name': 'My Name',
          'choice': 'A',
          'string_column_id': None,
          'string_column': None,
        }
        self.assertEqual(data, schema.deserialize(data))
        data = {
          'id': 1,
          'name': 'My Name.',
          'choice': 'B',
          'string_column_id': None,
          'string_column': None,
        }
        self.assertEqual(data, schema.deserialize(data))

    def test_relationship_validator(self):
        # Test collections.
        schema = colanderalchemy.get_schema(self.StringColumn)
        validator = colanderalchemy.RelationshipValidator(self.session,
                                                          self.EnumColumn)
        schema['enum_columns'].validator = validator
        data = {
          'id': 1,
          'name': None,
          'enum_columns': [1],
          'pk_column': None,
        }
        self.assertRaises(colander.Invalid, schema.deserialize, data)
        # Test references.
        schema = colanderalchemy.get_schema(self.EnumColumn)
        validator = colanderalchemy.RelationshipValidator(self.session,
                                                          self.StringColumn)
        schema['string_column'].validator = validator
        data = {
          'id': 1,
          'name': 'My Name.',
          'choice': 'B',
          'string_column_id': None,
          'string_column': 1,
        }
        self.assertRaises(colander.Invalid, schema.deserialize, data)
