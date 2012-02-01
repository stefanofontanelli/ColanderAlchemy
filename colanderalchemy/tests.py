#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

        self.StringColumn = StringColumn

    def test_string_column(self):
        schema = colanderalchemy.get_schema(self.StringColumn)
        assert colanderalchemy.get_registry(schema) != {}
