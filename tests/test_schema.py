# test_declarative.py
# Copyright (C) 2012 the ColanderAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of ColanderAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from colanderalchemy import (setup_schema,
                             SQLAlchemySchemaNode)
from sqlalchemy import (Column,
                        event,
                        ForeignKey,
                        inspect,
                        Unicode)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (mapper,
                            relationship)
from models import (Account,
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

    def test_add_nodes_exceptions(self):
        includes = ('email',)
        excludes = ('email',)
        self.assertRaises(ValueError, SQLAlchemySchemaNode, Account, includes, excludes)

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

        includes = [attr.key for attr in m.relationships]
        account_schema = SQLAlchemySchemaNode(Account, includes=includes)
        for attr in m.column_attrs:
            self.assertNotIn(attr.key, account_schema)

        for attr in m.relationships:
            self.assertIn(attr.key, account_schema)

    def test_imperative_excludes(self):
        m = inspect(Account)
        excludes = [attr.key for attr in m.column_attrs]
        account_schema = SQLAlchemySchemaNode(Account, excludes=excludes)
        for attr in m.column_attrs:
            self.assertNotIn(attr.key, account_schema)

        for attr in m.relationships:
            self.assertIn(attr.key, account_schema)

    def test_declarative_excludes(self):
        m = inspect(Address)
        address_schema = SQLAlchemySchemaNode(Address)
        self.assertNotIn('city', address_schema)
        self.assertNotIn('person', address_schema)
        for attr in m.attrs:
            if attr.key not in ('city', 'person'):
                self.assertIn(attr.key, address_schema)

    def test_imperative_colums_overrides(self):
        overrides = {
            'email': {
                'typ': colander.Integer
            }
        }
        account_schema = SQLAlchemySchemaNode(Account, overrides=overrides)
        self.assertNotEqual(isinstance(account_schema['email'].typ,
                                       colander.String),
                            True)
        self.assertEqual(isinstance(account_schema['email'].typ,
                                    colander.Integer),
                         True)
        overrides = {
            'email': {
                'children': []
            }
        }
        self.assertRaises(ValueError, SQLAlchemySchemaNode, Account, None, None, overrides)

    def test_declarative_colums_overrides(self):
        if sys.version_info[0] == 2 and sys.version_info[1] < 7:
            # This test fails in Python 2.6. Skip it.
            return

        key = SQLAlchemySchemaNode.sqla_info_key

        Base = declarative_base()

        class WrongColumnOverrides(Base):

            __tablename__ = 'WrongColumnOverrides'

            string = Column(Unicode(32), primary_key=True, info={key: {'name': 'Name'}})

        self.assertRaises(ValueError, SQLAlchemySchemaNode, WrongColumnOverrides)

    def test_imperative_relationships_overrides(self):
        overrides = {
            'person': {
                'name': 'Name'
            }
        }
        self.assertRaises(ValueError, SQLAlchemySchemaNode, Account, None, None, overrides)
        overrides = {
            'person': {
                'typ': colander.Integer
            }
        }
        self.assertRaises(ValueError, SQLAlchemySchemaNode, Account, None, None, overrides)
        overrides = {
            'person': {
                'children': [],
                'includes': ['id']
            },
        }
        schema = SQLAlchemySchemaNode(Account, overrides=overrides)
        self.assertEqual(schema['person'].children, [])
        overrides = {
            'person': {
                'includes': ['id']
            },
        }
        schema = SQLAlchemySchemaNode(Account, overrides=overrides)
        self.assertIn('id', schema['person'])
        self.assertEqual(len(schema['person'].children), 1)
        overrides = {
            'person': {
                'excludes': ['id']
            },
        }
        schema = SQLAlchemySchemaNode(Account, overrides=overrides)
        self.assertNotIn('id', schema['person'])

        overrides = {
            'addresses': {
                'overrides': {
                    'id': {
                        'typ': colander.Float
                    }
                }
            }
        }
        overrides = {
            'addresses': {
                'overrides': {
                    'id': {
                        'typ': colander.String
                    }
                }
            }
        }
        schema = SQLAlchemySchemaNode(Person, overrides=overrides)
        self.assertTrue(isinstance(schema['addresses'].children[0]['id'].typ, colander.String))

    def test_declarative_relationships_overrides(self):

        key = SQLAlchemySchemaNode.sqla_info_key
        base = declarative_base()

        class Model(base):
            __tablename__ = 'models'
            name = Column(Unicode(32), primary_key=True)
            description = Column(Unicode(128))

        class WrongOverrides(base):
            __tablename__ = 'WrongOverrides'
            name = Column(Unicode(32), primary_key=True)
            model_id = Column(Unicode(32), ForeignKey('models.name'))
            model = relationship(Model,
                                 info={
                                    key: {
                                        'children': [],
                                    }
                                })

        schema = SQLAlchemySchemaNode(WrongOverrides)
        self.assertEqual(schema['model'].children, [])

        class IncludesOverrides(base):
            __tablename__ = 'IncludesOverrides'
            name = Column(Unicode(32), primary_key=True)
            model_id = Column(Unicode(32), ForeignKey('models.name'))
            model = relationship(Model,
                                 info={
                                    key: {
                                        'includes': ['name']
                                    }
                                })
        schema = SQLAlchemySchemaNode(IncludesOverrides)
        self.assertEqual(set([node.name for node in schema['model']]), set(['name']))

        class ExcludesOverrides(base):
            __tablename__ = 'ExcludesOverrides'
            name = Column(Unicode(32), primary_key=True)
            model_id = Column(Unicode(32), ForeignKey('models.name'))
            model = relationship(Model,
                                 info={
                                    key: {
                                        'excludes': ['name']
                                    }
                                })
        schema = SQLAlchemySchemaNode(ExcludesOverrides)
        self.assertNotIn('name', schema['model'])

        class UseListOverrides(base):
            __tablename__ = 'UseListOverrides'
            name = Column(Unicode(32), primary_key=True)
            model_id = Column(Unicode(32), ForeignKey('models.name'))
            model = relationship(Model,
                                 info={
                                    key: {
                                        'children': [],
                                    }
                                }, uselist=True)
        schema = SQLAlchemySchemaNode(UseListOverrides)
        self.assertTrue(isinstance(schema['model'].typ, colander.Sequence))
        # Retrieve and check overrides kwarg.
        schema = SQLAlchemySchemaNode(Person)
        self.assertTrue(isinstance(schema['addresses'].children[0]['id'].typ, colander.Float))

    def test_dictify(self):
        import datetime
        overrides = {
            'person': {
                'includes': ['name', 'surname', 'gender', 'addresses'],
                'overrides': {
                    'addresses': {
                        'includes': ['street', 'city'],
                        'overrides': {
                            'city': {
                                'exclude': False
                            }
                        }
                    }
                }
            },
        }
        includes = ['email', 'enabled', 'created', 'timeout', 'person']
        schema = SQLAlchemySchemaNode(Account, includes=includes, overrides=overrides)
        #Add a non-SQLAlchemy field
        schema.add(colander.SchemaNode(colander.String, name='non_sql'))

        args = dict(street='My Street', city='My City')
        address = Address(**args)
        kws = dict(name='My Name', surname='My Surname', gender='M', addresses=[address])
        person = Person(**kws)
        params = dict(email='mailbox@domain.tld',
                      enabled=True,
                      created=datetime.datetime.now(),
                      timeout=datetime.time(hour=00, minute=00),
                      person=person)
        account = Account(**params)
        dictified = schema.dictify(account)
        kws['addresses'] = [args]
        params['person'] = kws
        self.assertEqual(dictified, params)
        for key in params:
            self.assertIn(key, dictified)
            if key == 'person':
                for k in kws:
                    self.assertIn(k, dictified[key])

    def test_clone(self):
        schema = SQLAlchemySchemaNode(Account)
        cloned = schema.clone()
        for attr in ['class_', 'includes', 'excludes', 'overrides', 'unknown']:
            self.assertEqual(getattr(schema, attr), getattr(cloned, attr))

        self.assertEqual([node.name for node in schema.children],
                         [node.name for node in cloned.children])

    def test_schemanode_arguments(self):
        """ Test that any arguments to SchemaNode are accepted.
        """
        schema = SQLAlchemySchemaNode(Account,
                                      widget='DummyWidget',
                                      title='Dummy',
                                      non_standard='Not a Colander arg')
        self.assertEqual(schema.widget, 'DummyWidget')
        self.assertEqual(schema.title, 'Dummy')
        self.assertEqual(schema.non_standard, 'Not a Colander arg')

    def test_read_mapping_configuration(self):
        """ Test using ``__colanderalchemy_config__`` for a mapped class.
        """
        schema = SQLAlchemySchemaNode(Account)
        self.assertEqual(schema.preparer, 'DummyPreparer')

        #Related models will be configured as well
        self.assertEqual(schema['person'].widget, 'DummyWidget')
        self.assertEqual(schema['person'].title, 'Person Object')

