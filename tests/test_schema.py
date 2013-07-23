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
from tests.models import (Account,
                          Person,
                          Address,
                          Group)
import colander
import datetime
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
        key = SQLAlchemySchemaNode.sqla_info_key
        Base = declarative_base()

        class WrongColumnOverrides(Base):
            __tablename__ = 'WrongColumnOverrides'
            string = Column(Unicode(32), primary_key=True, info={key: {'name': 'Name'}})

        self.assertRaises(ValueError, SQLAlchemySchemaNode, WrongColumnOverrides)
        
        """ SQLAlchemy gives sqlalchemy.exc.InvalidRequestError errors for
            subsequent tests because this mapper is not always garbage
            collected quick enough.  By removing the _configured_failed
            flag on the mapper this allows later tests to function
            properly.
        """
        try:
            del WrongColumnOverrides.__mapper__._configure_failed
        except AttributeError:
            pass

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
        Base = declarative_base()

        class Model(Base):
            __tablename__ = 'models'
            name = Column(Unicode(32), primary_key=True)
            description = Column(Unicode(128))

        #Fake model to avoid a race condition
        dummy = Model()

        class WrongOverrides(Base):
            __tablename__ = 'WrongOverrides'
            name = Column(Unicode(32), primary_key=True)
            model_id = Column(Unicode(32), ForeignKey('models.name'))
            model = relationship(Model,
                                 info={
                                    key: {
                                        'children': [],
                                    }
                                })

        #Fake model to avoid a race condition
        dummy2 = WrongOverrides()

        schema = SQLAlchemySchemaNode(WrongOverrides)
        self.assertEqual(schema['model'].children, [])

        class IncludesOverrides(Base):
            __tablename__ = 'IncludesOverrides'
            name = Column(Unicode(32), primary_key=True)
            model_id = Column(Unicode(32), ForeignKey('models.name'))
            model = relationship(Model,
                                 info={
                                    key: {
                                        'includes': ['name']
                                    }
                                })

        #Fake model to avoid a race condition
        dummy3 = IncludesOverrides()

        schema = SQLAlchemySchemaNode(IncludesOverrides)
        self.assertEqual(set([node.name for node in schema['model']]), set(['name']))

        class ExcludesOverrides(Base):
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

        class UseListOverrides(Base):
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

    def _prep_schema(self):
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
        return schema

    def test_dictify(self):
        schema = self._prep_schema()

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

    def test_objectify(self):
        """ Test converting a dictionary or data structure into objects.
        """
        dict_ = {'person': {'gender': 'M',
                            'surname': 'My Surname',
                            'addresses': [{'city': 'My City',
                                           'street': 'My Street'}],
                            'name': 'My Name'},
                 'enabled': True,
                 'email': 'mailbox@domain.tld',
                 'timeout': datetime.time(hour=0, minute=0),
                 'created': datetime.datetime.now(),
                 'foobar': 'a fake value' #Not present in schema
                }
        schema = self._prep_schema()

        objectified = schema.objectify(dict_)
        self.assertIsInstance(objectified, Account)
        self.assertEqual(objectified.email, 'mailbox@domain.tld')
        self.assertIsInstance(objectified.person, Person)
        self.assertEqual(objectified.person.name, 'My Name')
        self.assertFalse(hasattr(objectified, 'foobar'))

    def test_objectify_context(self):
        """ Test converting a data structure into objects, using a context.
        """
        dict_ = {'enabled': True,
                 'email': 'mailbox@domain.tld'}
        schema = self._prep_schema()

        class DummyContext(object):
            dummy_property = 'dummy'

        context = DummyContext()

        objectified = schema.objectify(dict_, context=context)

        #Must be the same object
        self.assertTrue(context is objectified)
        self.assertEqual(objectified.enabled, True)
        self.assertEqual(objectified.email, 'mailbox@domain.tld')
        self.assertEqual(objectified.dummy_property, 'dummy')


    def test_clone(self):
        schema = SQLAlchemySchemaNode(Account, dummy='dummy', dummy2='dummy2')
        cloned = schema.clone()
        for attr in ['class_', 'includes', 'excludes', 'overrides']:
            self.assertEqual(getattr(schema, attr), getattr(cloned, attr))
        self.assertEqual(cloned.kwargs, schema.kwargs)

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

    def test_missing_mapping_configuration(self):
        """ Test to check ``missing`` is set to an SQLAlchemy-suitable value.
        """
        schema = SQLAlchemySchemaNode(Account)
        self.assertIsNone(schema['person_id'].missing)
        self.assertIsNone(schema['person'].missing)
        deserialized = schema.deserialize({'email': 'test@example.com',
                                           'timeout': '09:44:33'})
        self.assertIsNone(deserialized['person_id'])
        self.assertIsNone(deserialized['person'])

    def test_relationship_mapping_configuration(self):
        """Test to ensure ``missing`` is set to required accordingly.
        """
        schema = SQLAlchemySchemaNode(Group)
        self.assertTrue(schema.required)
        self.assertEqual(schema.missing, colander.required)

        #Group must have a leader
        self.assertTrue(schema['leader'].required)
        self.assertEqual(schema['leader'].missing, colander.required)

        #Group must have an executive
        self.assertTrue(schema['executive'].required)
        self.assertEqual(schema['executive'].missing, colander.required)

        #Group may have members
        self.assertFalse(schema['members'].required)
        self.assertEqual(schema['members'].missing, [])
