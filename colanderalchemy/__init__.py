#!/usr/bin/env python
# -*- coding: utf-8 -*-

import colander
import collections
import logging
import sqlalchemy.orm
import sqlalchemy.orm.properties
import sqlalchemy.types


__colanderalchemy__ = '__colanderalchemy__'
log = logging.getLogger(__name__)


class Registry(object):

    def __init__(self, mapper):

        log.debug('Creating Registry ...')

        self.keys = [col.name for col in mapper.primary_key]
        self.fkeys = {}
        self.rkeys = {}
        self.fields = {}
        self.relationships = {}
        self.references = set()
        self.collections = set()

        for p in mapper.iterate_properties:

            if isinstance(p, sqlalchemy.orm.properties.ColumnProperty):

                self.fields[p.key] = p.columns[0]

            elif isinstance(p, sqlalchemy.orm.properties.RelationshipProperty):

                if callable(p.argument):
                    cls = p.argument()

                else:
                    cls = p.argument.class_

                self.relationships[p.key] = cls
                self.rkeys[p.key] = []
                for col in sqlalchemy.orm.class_mapper(cls).primary_key:
                    self.rkeys[p.key].append(col.name)

                if p.uselist:
                    self.collections.add(p.key)
                else:
                    self.references.add(p.key)
                    self.fkeys[p.key] = collections.OrderedDict()
                    for col in p._calculated_foreign_keys:
                        if col.table in mapper.tables:
                            for f in col.foreign_keys:
                                self.fkeys[p.key][col.name] = f.column.name

                    if not self.fkeys[p.key]:
                        self.fkeys.pop(p.key)
            else:
                msg = 'Unsupported property type: {}'.format(type(p))
                NotImplementedError(msg)

        log.debug('Keys: %s',
                  self.keys)
        log.debug('Foreign Keys: %s',
                  self.fkeys)
        log.debug('Fieds: %s, %s',
                  self.fields.keys(),
                  self.fields.values())
        log.debug('Relationships: %s, %s',
                  self.relationships.keys(),
                  self.relationships.values())
        log.debug('Relationships Keys: %s, %s',
                  self.rkeys.keys(),
                  self.rkeys.values())
        log.debug('References: %s',
                  self.references)
        log.debug('Collections: %s',
                  self.collections)


class Schema(object):

    def __init__(self, entity, session=None, excludes=None, nullables=None):
        """ Build a Colander Schema based on the SQLAlchemy mapped class.

            The structure serialized/deserialized by default schema is:
            {
                'col1_name': 'value_col_1',
                'col2_name': 'value_col_2',
                'fk1_name': 'value_fk1',
                'collection1': [],
                'collection2': [{'pk_name': 'pk_value'}],
            }
        """
        log.debug('Create schema for: %s', entity.__name__)
        # An entity's schema has the following structure:
        # {'attr1': value1, 'attr2': value2, ...}
        self.entity = entity
        mapper = sqlalchemy.orm.class_mapper(entity)
        self.registry = Registry(mapper)
        self.session = session
        excludes = excludes if excludes else set()
        nullables = nullables if nullables else {}

        self.impl = colander.SchemaNode(colander.Mapping())
        for name, column in self.registry.fields.iteritems():
            if name in excludes:
                continue
            node = self.get_schema_from_col(column, nullables.get(name, None))
            node.name = name
            self.impl.add(node)

        for name, rel in self.registry.relationships.iteritems():
            if name in excludes:
                continue
            collection = name in self.registry.collections
            node = self.get_schema_from_rel(rel, collection=collection)
            node.name = name
            self.impl.add(node)

    def get_schema_from_col(self, column, nullable=None):
        """ Build and return a Colander SchemaNode
            using information stored in the column.
        """

        validator = None
        # Add a default value for deserialized missing parameters.
        missing = None if column.default is None else column.default.arg
        if not column.nullable:
            missing = colander.required

        if isinstance(column.type, sqlalchemy.types.Boolean):
            type_ = colander.Boolean()

        elif isinstance(column.type, sqlalchemy.types.Date):
            type_ = colander.Date()

        elif isinstance(column.type, sqlalchemy.types.DateTime):
            type_ = colander.DateTime()

        elif isinstance(column.type, sqlalchemy.types.Enum):
            type_ = colander.String()
            validator = colander.OneOf(column.type.enums)

        elif isinstance(column.type, sqlalchemy.types.Float):
            type_ = colander.Float()

        elif isinstance(column.type, sqlalchemy.types.Integer):
            type_ = colander.Integer()

        elif isinstance(column.type, sqlalchemy.types.String):
            type_ = colander.String()
            validator = colander.Length(0, column.type.length)

        elif isinstance(column.type, sqlalchemy.types.Numeric):
            type_ = colander.Decimal()

        elif isinstance(column.type, sqlalchemy.types.Time):
            type_ = colander.Time()

        else:
            raise NotImplemented('Unknown type: %s' % column.type)

        # Overwrite default missing value when nullable is specified.
        if nullable == False:
            missing = colander.required

        elif nullable == True:
            missing = None

        return colander.SchemaNode(type_,
                                   name=column.name,
                                   validator=validator,
                                   missing=missing)

    def get_schema_from_rel(self, cls, collection=False):
        """ Build and return a Colander SchemaNode
            using information stored in the relationship property.
        """

        mapper = sqlalchemy.orm.class_mapper(cls)
        nodes = [self.get_schema_from_col(col) for col in mapper.primary_key]

        if collection:
            # xToMany relationships.
            type_ = colander.Sequence()
            missing = []
            default = colander.null
        else:
            # xToOne relationships.
            type_ = colander.Mapping()
            missing = None
            default = colander.null

        return colander.SchemaNode(type_,
                                   *nodes,
                                   missing=missing,
                                   default=default)

    def deserialize(self, data, colander_only=False):

        data = self.impl.deserialize(data)
        log.debug('Colander deserialized: %s', data)

        if colander_only:
            return data

        for name, cls in self.registry.relationships.iteritems():

            if (name not in data or not data[name]) and\
               name in self.registry.fkeys:
                data[name] = {}
                for fk, key in self.registry.fkeys[name].iteritems():
                    value = data.get(fk)
                    if not value is None:
                        data[name][key] = value

            if name in self.registry.references and data[name]:
                data[name] = self.deserialize_relationship(name,
                                                           cls,
                                                           data[name])

            elif name in self.registry.collections and data[name]:
                data[name] = [self.deserialize_relationship(name, cls, value)
                              for value in data[name]]

        return self.entity(**data)

    def deserialize_relationship(self, name, cls, data):
        query = self.session.query(cls)
        mapper = sqlalchemy.orm.class_mapper(cls)
        value = tuple([data[key.name] for key in mapper.primary_key])
        obj = query.get(value)
        if obj is None:
            msg = "The object in '%s' doesn't exists." % name
            raise colander.Invalid(self.impl[name],
                                   msg,
                                   value=data)
        return obj

    def serialize(self, obj, use_colander=True):

        if not isinstance(obj, self.entity):
            msg = "Invalid object: '%s'. Only '%s' objects can be serialized."
            raise TypeError(msg % (type(obj), self.entity.__name__))

        dict_ = {}
        for name in self.registry.fields.iterkeys():
            dict_[name] = getattr(obj, name)

        for name in self.registry.references:
            value = getattr(obj, name)
            if not value is None:
                value = self.serialize_relationship(value)
            if use_colander and value is None:
                continue
            dict_[name] = value

        for name in self.registry.collections:
            dict_[name] = [self.serialize_relationship(value)
                           for value in getattr(obj, name)]

        if use_colander:
            return self.impl.serialize(dict_)

        return dict_

    def serialize_relationship(self, obj):
        dict_ = {}
        for col in sqlalchemy.orm.object_mapper(obj).primary_key:
            dict_[col.name] = getattr(obj, col.name)
        return dict_
