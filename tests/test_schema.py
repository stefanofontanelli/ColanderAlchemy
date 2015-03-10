# test_schema.py
# Copyright (C) 2012 the ColanderAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of ColanderAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import datetime
import logging
import sys

import sqlalchemy
from sqlalchemy import (Column,
                        ForeignKey,
                        Unicode,
                        Integer,
                        BigInteger,
                        TIMESTAMP,
                        String,
                        Enum)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import (hybrid_property,
                                   hybrid_method)
from sqlalchemy.orm import (relationship,
                            synonym,
                            column_property,
                            aliased)
from sqlalchemy.sql.expression import (text,
                                       func,
                                       select)
from sqlalchemy.schema import DefaultClause
from sqlalchemy.types import TypeDecorator
import colander

from colanderalchemy import SQLAlchemySchemaNode
from tests.models import (Account,
                          Person,
                          Address,
                          Group,
                          has_unique_addresses)

if sys.version_info[0] == 2 and sys.version_info[1] < 7:
    # In Python < 2.7 use unittest2.
    import unittest2 as unittest
else:
    import unittest

logging.basicConfig(level=logging.WARNING)
log = logging.getLogger(__name__)


class TestsSQLAlchemySchemaNode(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_setup_schema(self):
        for cls in [Account, Person, Address]:
            self.assertIsInstance(cls.__colanderalchemy__,
                                  SQLAlchemySchemaNode)

    def test_add_nodes_exceptions(self):
        includes = ('email',)
        excludes = ('email',)
        self.assertRaises(ValueError, SQLAlchemySchemaNode, Account,
                          includes, excludes)

    def test_default_strategy_for_columns_and_relationships_include_all(self):
        account_schema = SQLAlchemySchemaNode(Account)
        m = sqlalchemy.inspect(Account)
        for attr in m.attrs:
            self.assertIn(attr.key, account_schema)

    def test_default_strategy_for_included_relationships_schema(self):
        account_schema = SQLAlchemySchemaNode(Account)
        m = sqlalchemy.inspect(Person)
        for attr in m.column_attrs:
            self.assertIn(attr.key, account_schema['person'])

        for attr in m.relationships:
            self.assertNotIn(attr.key, account_schema['person'])

    def test_imperative_includes(self):
        m = sqlalchemy.inspect(Account)
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
        m = sqlalchemy.inspect(Account)
        excludes = [attr.key for attr in m.column_attrs]
        account_schema = SQLAlchemySchemaNode(Account, excludes=excludes)
        for attr in m.column_attrs:
            self.assertNotIn(attr.key, account_schema)

        for attr in m.relationships:
            self.assertIn(attr.key, account_schema)

    def test_declarative_excludes(self):
        m = sqlalchemy.inspect(Address)
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
        self.assertTrue(
            isinstance(account_schema['email'].typ, colander.Integer)
        )
        overrides = {
            'email': {
                'name': 'Name'
            }
        }
        self.assertRaises(ValueError, SQLAlchemySchemaNode, Account,
                          None, None, overrides)

        overrides = {
            'email': {
                'children': []
            }
        }
        # following shouldn't raise an exception allowing the test to pass
        SQLAlchemySchemaNode(Account, None, None, overrides)

    def test_declarative_colums_overrides(self):
        key = SQLAlchemySchemaNode.sqla_info_key
        Base = declarative_base()

        class WrongColumnOverrides(Base):
            __tablename__ = 'WrongColumnOverrides'
            string = Column(Unicode(32), primary_key=True,
                            info={key: {'name': 'Name'}})

        self.assertRaises(ValueError, SQLAlchemySchemaNode,
                          WrongColumnOverrides)

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
        self.assertRaises(ValueError, SQLAlchemySchemaNode, Account,
                          None, None, overrides)
        overrides = {
            'person': {
                'typ': colander.Integer
            }
        }
        self.assertRaises(ValueError, SQLAlchemySchemaNode, Account,
                          None, None, overrides)
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
        self.assertTrue(isinstance(
            schema['addresses'].children[0]['id'].typ,
            colander.String
        ))

    def test_declarative_relationships_overrides(self):
        key = SQLAlchemySchemaNode.sqla_info_key
        Base = declarative_base()

        class Model(Base):
            __tablename__ = 'models'
            name = Column(Unicode(32), primary_key=True)
            description = Column(Unicode(128))

        # Fake model to avoid a race condition
        dummy = Model()

        class WrongOverrides(Base):
            __tablename__ = 'WrongOverrides'
            name = Column(Unicode(32), primary_key=True)
            model_id = Column(Unicode(32), ForeignKey('models.name'))
            model = relationship(
                Model,
                info={
                    key: {
                        'children': [],
                    }
                }
            )

        # Fake model to avoid a race condition
        dummy2 = WrongOverrides()

        schema = SQLAlchemySchemaNode(WrongOverrides)
        self.assertEqual(schema['model'].children, [])

        class IncludesOverrides(Base):
            __tablename__ = 'IncludesOverrides'
            name = Column(Unicode(32), primary_key=True)
            model_id = Column(Unicode(32), ForeignKey('models.name'))
            model = relationship(
                Model,
                info={
                    key: {
                        'includes': ['name']
                    }
                }
            )

        # Fake model to avoid a race condition
        dummy3 = IncludesOverrides()

        schema = SQLAlchemySchemaNode(IncludesOverrides)
        self.assertEqual(set([node.name for node in schema['model']]),
                         set(['name']))

        class ExcludesOverrides(Base):
            __tablename__ = 'ExcludesOverrides'
            name = Column(Unicode(32), primary_key=True)
            model_id = Column(Unicode(32), ForeignKey('models.name'))
            model = relationship(
                Model,
                info={
                    key: {
                        'excludes': ['name']
                    }
                }
            )
        schema = SQLAlchemySchemaNode(ExcludesOverrides)
        self.assertNotIn('name', schema['model'])

        class UseListOverrides(Base):
            __tablename__ = 'UseListOverrides'
            name = Column(Unicode(32), primary_key=True)
            model_id = Column(Unicode(32), ForeignKey('models.name'))
            model = relationship(
                Model,
                info={
                    key: {
                        'children': [],
                    }
                },
                uselist=True
            )
        schema = SQLAlchemySchemaNode(UseListOverrides)
        self.assertTrue(isinstance(schema['model'].typ, colander.Sequence))
        # Retrieve and check overrides kwarg.
        schema = SQLAlchemySchemaNode(Person)
        self.assertTrue(isinstance(
            schema['addresses'].children[0]['id'].typ,
            colander.Float
        ))

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
        schema = SQLAlchemySchemaNode(Account, includes=includes,
                                      overrides=overrides)
        # Add a non-SQLAlchemy field
        schema.add(colander.SchemaNode(
            colander.String(),
            name='non_sql',
            missing=colander.drop
        ))
        return schema

    def test_dictify(self):
        """ Test SQLAlchemySchemaNode.dictify(obj)
        """
        schema = self._prep_schema()

        address_args = dict(street='My Street', city='My City')
        address = Address(**address_args)

        person_args = dict(name='My Name', surname='My Surname',
                           gender='M', addresses=[address])
        person = Person(**person_args)

        account_args = dict(email='mailbox@domain.tld',
                            enabled=True,
                            created=datetime.datetime.now(),
                            timeout=datetime.time(hour=1, minute=0),
                            person=person)
        account = Account(**account_args)

        appstruct = schema.dictify(account)

        person_args['addresses'] = [address_args]
        account_args['person'] = person_args
        self.assertEqual(appstruct, account_args)
        for account_key in account_args:
            self.assertIn(account_key, appstruct)
            if account_key == 'person':
                for person_key in person_args:
                    self.assertIn(person_key, appstruct[account_key])
                    if person_key == 'addresses':
                        for address_key in address_args:
                            self.assertIn(
                                address_key,
                                appstruct[account_key][person_key][0]
                            )

        # test that you can serialize this appstruct and you get
        #  the same result when you deserialize
        cstruct = schema.serialize(appstruct=appstruct)
        newappstruct = schema.deserialize(cstruct)
        self.assertEqual(appstruct, newappstruct)

    def test_dictify_with_null(self):
        """ Test SQLAlchemySchemaNode.dictify(obj) with null values
        and show that result is a valid appstruct for the given schema
        """
        Base = declarative_base()

        class Sensor(Base):
            __tablename__ = 'sensor'
            sensor_id = Column(Integer, primary_key=True)
            institution_id = Column(Integer, nullable=True)
            sensor_label = Column(String, nullable=True)

        sensor = Sensor(
            sensor_id=3,
            institution_id=None,
            sensor_label=None,
        )

        schema = SQLAlchemySchemaNode(Sensor)
        appstruct = schema.dictify(sensor)
        cstruct = schema.serialize(appstruct=appstruct)
        newappstruct = schema.deserialize(cstruct)
        newobj = schema.objectify(appstruct)

        self.assertEqual(appstruct, newappstruct)
        self.assertEqual(sensor.sensor_id, newobj.sensor_id)
        self.assertEqual(sensor.institution_id, newobj.institution_id)
        self.assertEqual(sensor.sensor_label, newobj.sensor_label)

    def test_objectify(self):
        """ Test converting a dictionary or data structure into objects.
        """
        dict_ = {
            'person': {
                'gender': 'M',
                'surname': 'My Surname',
                'addresses': [{
                    'city': 'My City',
                    'street': 'My Street'
                }],
                'name': 'My Name'
            },
            'enabled': True,
            'email': 'mailbox@domain.tld',
            'timeout': datetime.time(hour=0, minute=0),
            'created': datetime.datetime.now(),
            'foobar': 'a fake value'  # Not present in schema
        }
        schema = self._prep_schema()

        objectified = schema.objectify(dict_)
        self.assertIsInstance(objectified, Account)
        self.assertEqual(objectified.email, 'mailbox@domain.tld')
        self.assertIsInstance(objectified.person, Person)
        self.assertEqual(objectified.person.name, 'My Name')
        self.assertFalse(hasattr(objectified, 'foobar'))

    def test_null_issues(self):
        """ Make sure nullable values are set properly when null
        
        #42 introduced an issue where values may not have been properly
        set if the value is supposed to be set to null
        """
        Base = declarative_base()

        class Person(Base):
            __tablename__ = 'person'
            id = Column(Integer, primary_key=True)
            fullname = Column(String, nullable=True)
            age = Column(Integer, nullable=True)

        schema = SQLAlchemySchemaNode(Person)

        person = Person(
            id=7,
            fullname="Joe Smith",
            age=35,
        )

        # dict coming from a form submission
        update_cstruct = {
            'id': '7',
            'fullname': '',
            'age': '',
        }
        update_appstruct = schema.deserialize(update_cstruct)
        schema.objectify(update_appstruct, context=person)

        self.assertEqual(person.id, 7)
        self.assertEqual(person.fullname, None)
        self.assertEqual(person.age, None)

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

        # Must be the same object
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
        self.assertEqual(schema.typ.unknown, 'raise')

        # Related models will be configured as well
        self.assertEqual(schema['person'].widget, 'DummyWidget')
        self.assertEqual(schema['person'].title, 'Person Object')

    def test_missing_mapping_configuration(self):
        """ Test to check ``missing`` is set to an SQLAlchemy-suitable value.
        """
        schema = SQLAlchemySchemaNode(Account)
        self.assertEqual(schema['person_id'].missing, colander.null)
        self.assertEqual(schema['person'].missing, [])
        deserialized = schema.deserialize({'email': 'test@example.com',
                                           'timeout': '09:44:33'})
        self.assertEqual(deserialized['person_id'], colander.null)
        self.assertEqual(deserialized['person'], [])

    def test_relationship_mapping_configuration(self):
        """Test to ensure ``missing`` is set to required accordingly.
        """
        schema = SQLAlchemySchemaNode(Group)
        self.assertTrue(schema.required)
        self.assertEqual(schema.missing, colander.required)

        # Group must have a leader
        self.assertTrue(schema['leader'].required)
        self.assertEqual(schema['leader'].missing, colander.required)

        # Group must have an executive
        self.assertTrue(schema['executive'].required)
        self.assertEqual(schema['executive'].missing, colander.required)

        # Group may have members
        self.assertFalse(schema['members'].required)
        self.assertEqual(schema['members'].missing, [])

    def test_relationship_declarative_configuration(self):
        """ Ensure relationship mapping correctly applies configuration.

        A one-to-many relationship (use_list in SQLAlchemy) maps to a Sequence
        of Mapping objects in Colander. Declarative settings applied to the
        relationship in SQLAlchemy should apply only to the outer Sequence and
        not automatically be applied to the underlying Mapping.  Typically,
        one would use ``__colanderalchemy_config__`` on the related class
        to configure the Mapping.
        """
        schema = SQLAlchemySchemaNode(Person)

        # Settings should be applied to outer Sequence only
        addresses = schema['addresses']
        self.assertEqual(addresses.title, 'Your addresses')
        self.assertEqual(addresses.validator, has_unique_addresses)
        address_mapping = addresses.children[0]
        self.assertEqual(address_mapping.title, 'address')
        self.assertIsNone(address_mapping.validator)

        # Underlying Mapping should have independent settings applied
        self.assertEqual(address_mapping.description,
                         'A location associated with a person.')
        self.assertEqual(address_mapping.widget, 'dummy')

    def test_defaultmissing_primarykey(self):
        """Ensure proper handling of empty values on primary keys
        """
        Base = declarative_base()

        class User(Base):
            __tablename__ = 'user'
            # the follwing is automatically made autoincrement=True
            id = Column(Integer, primary_key=True)

        schema = SQLAlchemySchemaNode(User)

        # from <FORM> result into SQLA; tests missing
        self.assertEqual(schema['id'].missing, colander.drop)
        deserialized = schema.deserialize({})
        self.assertNotIn('id', deserialized)

        # from SQLA result into <FORM>; tests default
        self.assertEqual(schema['id'].default, colander.null)
        serialized = schema.serialize({})
        self.assertIn('id', serialized)
        self.assertEqual(serialized['id'], colander.null)

        class Widget(Base):
            __tablename__ = 'widget'
            id = Column(String, primary_key=True)

        schema = SQLAlchemySchemaNode(Widget)

        # from <FORM> result into SQLA; tests missing
        self.assertEqual(schema['id'].missing, colander.required)
        self.assertRaises(colander.Invalid, schema.deserialize, {})

        # from SQLA result into <FORM>; tests default
        self.assertEqual(schema['id'].default, colander.null)
        serialized = schema.serialize({})
        self.assertIn('id', serialized)
        self.assertEqual(serialized['id'], colander.null)

    def test_default_clause(self):
        """Test proper handling of default and server_default values
        """
        Base = declarative_base()

        def give_me_three():
            return 3

        class Patient(Base):
            __tablename__ = 'patient'
            # default= is equivalent to ColumnDefault()
            # server_default= is equivalent to DefaultClause()
            id = Column(
                BigInteger(),
                default=text("round(3.14159)"),
                primary_key=True,
                autoincrement=False
            )
            received_timestamp = Column(
                TIMESTAMP,
                server_default=func.now(),
                nullable=False
            )
            some_number = Column(
                Integer,
                DefaultClause('3'),
                nullable=False
            )
            scalar_number = Column(
                Integer,
                default=3,
                nullable=False
            )
            pyfunc_test = Column(
                Integer,
                default=give_me_three,
                nullable=False
            )

        schema = SQLAlchemySchemaNode(Patient)

        '''
        Conceivably you should be able to test DefaultClause for a
        scalar type value and use it as a default/missing in Colander.
        However, the value is interpreted by the backend engine and
        it could be interpreted by it in an unexpected way.  For this
        reason we drop the value and let the backend handle it.
        '''

        # from <FORM> result into SQLA; tests missing
        self.assertEqual(schema['id'].missing, colander.drop)
        self.assertEqual(schema['received_timestamp'].missing, colander.drop)
        self.assertEqual(schema['some_number'].missing, colander.drop)
        self.assertEqual(schema['scalar_number'].missing, 3)
        self.assertEqual(schema['pyfunc_test'].missing, colander.drop)
        deserialized = schema.deserialize({})
        self.assertIn('scalar_number', deserialized)
        self.assertEqual(deserialized['scalar_number'], 3)
        self.assertNotIn('pyfunc_test', deserialized)

        # from SQLA result into <FORM>; tests default
        self.assertEqual(schema['id'].default, colander.null)
        self.assertEqual(schema['received_timestamp'].default, colander.null)
        self.assertEqual(schema['some_number'].default, colander.null)
        self.assertEqual(schema['scalar_number'].default, 3)
        self.assertEqual(schema['pyfunc_test'].default, colander.null)
        serialized = schema.serialize({})
        self.assertIn('id', serialized)
        self.assertEqual(serialized['id'], colander.null)
        self.assertIn('received_timestamp', serialized)
        self.assertEqual(serialized['received_timestamp'], colander.null)
        self.assertIn('some_number', serialized)
        self.assertEqual(serialized['some_number'], colander.null)
        self.assertIn('scalar_number', serialized)
        self.assertEqual(serialized['scalar_number'], str(3))
        self.assertIn('pyfunc_test', serialized)
        self.assertEqual(serialized['pyfunc_test'], colander.null)

    def test_unsupported_column_property(self):
        """
        Issue #58 and #61 - ColanderAlchemy throws when encountering
        ColumnProperty without a Column but e.g. an SQL Query
        for examples see
        http://docs.sqlalchemy.org/en/rel_0_9/orm/mapper_config.html#using-column-property-for-column-level-options

        ColanderAlchemy should ignore ColumnProperty which
        doesn't contain a valid Column
        """
        Base = declarative_base()

        # example taken from SQLAlchemy docs
        class Address(Base):
            __tablename__ = 'address'
            id = Column(Integer, primary_key=True)
            user_id = Column(Integer, ForeignKey('user.id'))

        class User(Base):
            __tablename__ = 'user'
            id = Column(Integer, primary_key=True)
            firstname = Column(String(50))
            lastname = Column(String(50))
            fullname = column_property(firstname + " " + lastname)
            address_count = column_property(
                select([func.count(Address.id)]).
                where(Address.user_id == id).
                correlate_except(Address)
            )

        schema = SQLAlchemySchemaNode(User)

        self.assertIn('id', schema)
        self.assertIn('firstname', schema)
        self.assertNotIn('fullname', schema)
        self.assertNotIn('address_count', schema)

    def test_unsupported_column_types(self):
        """
        Issue #35 - ColanderAlchemy throws when encountering synonyms

        ColanderAlchemy should ignore synonyms
        """
        Base = declarative_base()

        # example taken from SQLAlchemy docs
        class MyClass(Base):
            __tablename__ = 'my_table'

            id = Column(Integer, primary_key=True)
            job_status = Column(String(50))

            status = synonym("job_status")

        schema = SQLAlchemySchemaNode(MyClass)

        self.assertIn('id', schema)
        self.assertIn('job_status', schema)
        self.assertNotIn('status', schema)

    def test_aliased_view(self):
        """tests aliased view that was broken in 0.3.1
        """
        Base = declarative_base()

        class Person(Base):
            __tablename__ = 'person'

            id = Column(Integer, primary_key=True)
            parent_id = Column(Integer, ForeignKey('person.id'))

        class ParentView(Base):
            _parent_table = Person.__table__
            _child_table = aliased(_parent_table)

            __mapper_args__ = {
                'primary_key': [_child_table.c.id],
                'include_properties': [_child_table.c.id],
            }

            __table__ = _parent_table.join(
                _child_table,
                _child_table.c.parent_id == _parent_table.c.id
            )

        schema = SQLAlchemySchemaNode(ParentView)
        self.assertIn('id', schema)

    def test_hybrid_attributes(self):
        Base = declarative_base()

        class Interval(Base):
            __tablename__ = 'interval'

            id = Column(Integer, primary_key=True, info={'id': 'id'})
            start = Column(Integer, nullable=False, info={'start': 'start'})
            end = Column(Integer, nullable=False, info={'end': 'end'})

            def __init__(self, start, end):
                self.start = start
                self.end = end

            @hybrid_property
            def length(self):
                return self.end - self.start

            @hybrid_method
            def contains(self, point):
                return (self.start <= point) & (point < self.end)

            @hybrid_method
            def intersects(self, other):
                return self.contains(other.start) | self.contains(other.end)

            @length.setter
            def length(self, value):
                self.end = self.start + value

        schema = SQLAlchemySchemaNode(Interval)

        self.assertIn('id', schema)
        self.assertIn('start', schema)
        self.assertIn('end', schema)
        self.assertNotIn('length', schema)
        self.assertNotIn('contains', schema)
        self.assertNotIn('intersects', schema)

    def test_doc_example_deform(self):
        """
        Test 'using ColanderAlchemy with Deform' example found
        in docs/source/deform.rst
        """
        Base = declarative_base()

        class Phone(Base):
            __tablename__ = 'phones'

            person_id = Column(Integer, ForeignKey('persons.id'),
                               primary_key=True)
            number = Column(Unicode(128), primary_key=True)
            location = Column(Enum('home', 'work'))

        class Person(Base):
            __tablename__ = 'persons'

            id = Column(Integer, primary_key=True)
            name = Column(Unicode(128), nullable=False)
            surname = Column(Unicode(128), nullable=False)
            phones = relationship(Phone)

        schema = SQLAlchemySchemaNode(Person)

        # because of naming clashes, we need to do this in another function
        def generate_colander():
            class Phone(colander.MappingSchema):
                person_id = colander.SchemaNode(colander.Int())
                number = colander.SchemaNode(
                    colander.String(),
                    validator=colander.Length(0, 128)
                )
                location = colander.SchemaNode(
                    colander.String(),
                    validator=colander.OneOf(['home', 'work']),
                    missing=colander.null
                )

            class Phones(colander.SequenceSchema):
                phones = Phone(missing=[])

            class Person(colander.MappingSchema):
                id = colander.SchemaNode(colander.Int(),
                                         missing=colander.drop)
                name = colander.SchemaNode(
                    colander.String(),
                    validator=colander.Length(0, 128)
                )
                surname = colander.SchemaNode(
                    colander.String(),
                    validator=colander.Length(0, 128)
                )
                phones = Phones(missing=[])

            return Person()

        schema2 = generate_colander()

        self.is_equal_schema(schema, schema2)

    def test_doc_example_less_boilerplate(self):
        """
        Test 'Examples: Less boilerplate' example
        found in docs/source/examples.rst
        """
        Base = declarative_base()

        class Phone(Base):
            __tablename__ = 'phones'

            person_id = Column(Integer, ForeignKey('persons.id'),
                               primary_key=True)
            number = Column(Unicode(128), primary_key=True)
            location = Column(Enum('home', 'work'))

        class Friend(Base):
            __tablename__ = 'friends'

            person_id = Column(Integer, ForeignKey('persons.id'),
                               primary_key=True)
            friend_of = Column(Integer, ForeignKey('persons.id'),
                               primary_key=True)
            rank = Column(Integer, default=0)

        class Person(Base):
            __tablename__ = 'persons'

            id = Column(Integer, primary_key=True)
            name = Column(Unicode(128), nullable=False)
            surname = Column(Unicode(128), nullable=False)
            gender = Column(Enum('M', 'F'))
            age = Column(Integer)
            phones = relationship(Phone)
            friends = relationship(Friend, foreign_keys=[Friend.person_id])

        schema = SQLAlchemySchemaNode(Person)

        # because of naming clashes, we need to do this in another function
        def generate_colander():
            class Friend(colander.MappingSchema):
                person_id = colander.SchemaNode(colander.Int())
                friend_of = colander.SchemaNode(colander.Int())
                rank = colander.SchemaNode(colander.Int(),
                                           missing=0,
                                           default=0)

            class Phone(colander.MappingSchema):
                person_id = colander.SchemaNode(colander.Int())
                number = colander.SchemaNode(
                    colander.String(),
                    validator=colander.Length(0, 128)
                )
                location = colander.SchemaNode(
                    colander.String(),
                    validator=colander.OneOf(['home', 'work']),
                    missing=colander.null
                )

            class Friends(colander.SequenceSchema):
                friends = Friend(missing=[])

            class Phones(colander.SequenceSchema):
                phones = Phone(missing=[])

            class Person(colander.MappingSchema):
                id = colander.SchemaNode(
                    colander.Int(),
                    missing=colander.drop
                )
                name = colander.SchemaNode(
                    colander.String(),
                    validator=colander.Length(0, 128)
                )
                surname = colander.SchemaNode(
                    colander.String(),
                    validator=colander.Length(0, 128)
                )
                gender = colander.SchemaNode(
                    colander.String(),
                    validator=colander.OneOf(['M', 'F']),
                    missing=colander.null
                )
                age = colander.SchemaNode(
                    colander.Int(),
                    missing=colander.null
                )
                phones = Phones(missing=[])
                friends = Friends(missing=[])

            return Person()

        schema2 = generate_colander()

        self.is_equal_schema(schema, schema2)

    def test_doc_example_Configuring_within_SQLAlchemy(self):
        """
        Test 'Configuring within SQLAlchemy models' example
        found in docs/source/customization.rst
        """

        Base = declarative_base()

        class Person(Base):
            __tablename__ = 'person'
            # Fully customised schema node
            id = Column(sqlalchemy.Integer,
                        primary_key=True,
                        info={'colanderalchemy': {
                            'typ': colander.Float(),
                            'title': 'Person ID',
                            'description': 'The Person identifier.',
                            'widget': 'Empty Widget'
                        }})
            # Explicitly set as a default field
            name = Column(sqlalchemy.Unicode(128),
                          nullable=False,
                          info={'colanderalchemy': {
                              'default': colander.required
                          }})
            # Explicitly excluded from resulting schema
            surname = Column(sqlalchemy.Unicode(128),
                             nullable=False,
                             info={'colanderalchemy': {'exclude': True}})

        schema = SQLAlchemySchemaNode(Person)

        # because of naming clashes, we need to do this in another function
        def generate_colander():
            class Person(colander.MappingSchema):
                id = colander.SchemaNode(colander.Float(),
                                         title='Person ID',
                                         description='The Person identifier.',
                                         missing=colander.drop,
                                         widget='Empty Widget')
                name = colander.SchemaNode(colander.String(),
                                           validator=colander.Length(0, 128),
                                           default=colander.required)

            return Person()

        schema2 = generate_colander()

        self.is_equal_schema(schema, schema2)

    def is_equal_schema(self, schema, schema2, schema_path=None):
        '''method to compare two colander schema for testing
        purposes

         - does not compare preparer, validator, after_bind, missing_msg
         - does not do a proper comparison on widgets, but it is
           sufficient for this test suite
        '''

        if schema_path is None:
            schema_path = []
        else:
            schema_path.append(schema.name)
        self.assertEqual(schema.name, schema2.name)
        self.assertEqual(type(schema.typ), type(schema2.typ),
                         msg=".".join(schema_path))
        self.assertEqual(schema.title, schema2.title,
                         msg=".".join(schema_path))
        self.assertEqual(schema.description, schema2.description,
                         msg=".".join(schema_path))
        self.assertEqual(schema.missing, schema2.missing,
                         msg=".".join(schema_path))
        self.assertEqual(schema.default, schema2.default,
                         msg=".".join(schema_path))
        self.assertEqual(schema.widget, schema2.widget,
                         msg=".".join(schema_path))

        self.assertEqual(len(schema.children), len(schema2.children))

        # test children and test that they're in the right order
        for i, node in enumerate(schema.children):
            self.assertEqual(node.name, schema2.children[i].name,
                             msg=".".join(schema_path))
            self.is_equal_schema(node, schema2.children[i], schema_path[:])

    def test_specify_order_fields(self):
        """
        Test this issue:
        How to specify the order in which fields should be displayed ? #45
        """
        Base = declarative_base()

        # example taken from SQLAlchemy docs
        class MyClass(Base):
            __tablename__ = 'my_table'

            id = Column(Integer, primary_key=True)
            job_status = Column(String(50))

            status = synonym("job_status")

        schema = SQLAlchemySchemaNode(MyClass,
                                      includes=['foo', 'job_status', 'id'])
        self.assertEqual(['job_status', 'id'], [x.name for x in schema])
        self.assertNotIn('foo', schema)

        schema = SQLAlchemySchemaNode(MyClass,
                                      includes=['id', 'foo', 'job_status'])
        self.assertEqual(['id', 'job_status'], [x.name for x in schema])
        self.assertNotIn('foo', schema)

    def test_non_text_includes(self):
        Base = declarative_base()

        # example taken from SQLAlchemy docs
        class MyClass(Base):
            __tablename__ = 'my_table'

            id = Column(Integer, primary_key=True)
            job_status = Column(String(50))

            status = synonym("job_status")
        typ = colander.String()
        column = colander.SchemaNode(typ,
                                     name='customfield')
        schema = SQLAlchemySchemaNode(MyClass,
                                      includes=[
                                          'foo',
                                          'job_status',
                                          column,
                                          'id'
                                      ])
        self.assertEqual(['job_status', 'customfield', 'id'],
                         [x.name for x in schema])
        self.assertNotIn('foo', schema)

    def test_typedecorator_overwrite(self):
        key = SQLAlchemySchemaNode.sqla_info_key
        Base = declarative_base()

        class MyIntType(TypeDecorator):
            impl = Integer
            __colanderalchemy_config__ = {'typ': colander.String()}

        def string_validator(node, value):
            """A dummy validator."""
            pass

        class MyString(TypeDecorator):
            impl = Unicode
            __colanderalchemy_config__ = {'validator': string_validator}

        class World(Base):
            __tablename__ = 'world'
            id = Column(Integer, primary_key=True)
            not_a_number = Column(MyIntType)
            number = Column(MyIntType, info={key:
                                             {'typ': colander.Integer}})
            name = Column(MyString(5))

        world_schema = SQLAlchemySchemaNode(World)

        self.assertTrue(
            isinstance(world_schema['not_a_number'].typ, colander.String))
        # should be overwritten by the key
        self.assertFalse(isinstance(
            world_schema['number'].typ, colander.String
        ))

        # test if validator is not overwritten by ColanderAlchemy
        self.assertEqual(world_schema['name'].validator, string_validator)

    def test_example_typedecorator_overwrite(self):
        Base = declarative_base()

        class Email(TypeDecorator):
            impl = Unicode
            __colanderalchemy_config__ = {'validator': colander.Email}

        class User(Base):
            __tablename__ = 'user'
            id = Column(Integer, primary_key=True)
            email = Column(Email, nullable=False)
            second_email = Column(Email)

        schema = SQLAlchemySchemaNode(User)

        # because of naming clashes, we need to do this in another function
        def generate_colander():
            class User(colander.MappingSchema):
                id = colander.SchemaNode(colander.Integer(),
                                         missing=colander.drop)
                email = colander.SchemaNode(colander.String(),
                                            validator=colander.Email())
                second_email = colander.SchemaNode(colander.String(),
                                                   validator=colander.Email(),
                                                   missing=colander.null)

            return User()

        schema2 = generate_colander()

        self.is_equal_schema(schema, schema2)

    def test_validator_typedecorator_override(self):
        Base = declarative_base()

        def location_validator(value, node):
            """A dummy validator."""
            pass

        class LocationEnum(TypeDecorator):
            impl = Enum
            __colanderalchemy_config__ = {'validator': location_validator}

        class LocationString(TypeDecorator):
            impl = String
            __colanderalchemy_config__ = {'validator': location_validator}

        class House(Base):
            __tablename__ = 'house'
            id = Column(Integer, primary_key=True)
            door = Column(LocationEnum(['back', 'front']))
            window = Column(LocationString(128))

        schema = SQLAlchemySchemaNode(House)

        self.assertEqual(schema['door'].validator, location_validator)
        self.assertEqual(schema['window'].validator, location_validator)

    def test_default_typedecorator_override(self):
        Base = declarative_base()

        class MyInt(TypeDecorator):
            impl = Integer
            __colanderalchemy_config__ = {'default': 42}

        class Numbers(Base):
            __tablename__ = 'numbers'
            id = Column(Integer, primary_key=True)
            number1 = Column(MyInt)

        self.assertRaises(ValueError, SQLAlchemySchemaNode, Numbers,
                          None, None, None)

        """ SQLAlchemy gives sqlalchemy.exc.InvalidRequestError errors for
            subsequent tests because this mapper is not always garbage
            collected quick enough.  By removing the _configured_failed
            flag on the mapper this allows later tests to function
            properly.
        """
        try:
            del Numbers.__mapper__._configure_failed
        except AttributeError:
            pass

    def test_missing_typedecorator_override(self):
        Base = declarative_base()

        class MyInt(TypeDecorator):
            impl = Integer
            __colanderalchemy_config__ = {'missing': 42}

        class Numbers(Base):
            __tablename__ = 'numbers'
            id = Column(Integer, primary_key=True)
            number1 = Column(MyInt)

        self.assertRaises(ValueError, SQLAlchemySchemaNode, Numbers,
                          None, None, None)

        """ SQLAlchemy gives sqlalchemy.exc.InvalidRequestError errors for
            subsequent tests because this mapper is not always garbage
            collected quick enough.  By removing the _configured_failed
            flag on the mapper this allows later tests to function
            properly.
        """
        try:
            del Numbers.__mapper__._configure_failed
        except AttributeError:
            pass

    def test_typedecorator_override_name(self):
        Base = declarative_base()

        class WrongType(TypeDecorator):
            impl = String
            __colanderalchemy_config__ = {'name': 'Wrong!'}

        class BadTable(Base):
            __tablename__ = 'badtable'
            nasty_column = Column(WrongType, primary_key=True)

        self.assertRaises(ValueError, SQLAlchemySchemaNode, BadTable,
                          None, None, None)

        """ SQLAlchemy gives sqlalchemy.exc.InvalidRequestError errors for
            subsequent tests because this mapper is not always garbage
            collected quick enough.  By removing the _configured_failed
            flag on the mapper this allows later tests to function
            properly.
        """
        try:
            del BadTable.__mapper__._configure_failed
        except AttributeError:
            pass
