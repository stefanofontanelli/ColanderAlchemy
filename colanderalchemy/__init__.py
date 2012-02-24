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

        self.keys = mapper.primary_key
        self.fields = {}
        self.relationships = {}
        self.relationships_keys = {}
        self.references = {}
        self.references_keys = {}
        self.collections = {}

        for p in mapper.iterate_properties:

            if isinstance(p, sqlalchemy.orm.properties.ColumnProperty):

                self.fields[p.key] = p.columns[0]

            elif isinstance(p, sqlalchemy.orm.properties.RelationshipProperty):

                if callable(p.argument):
                    cls = p.argument()

                else:
                    cls = p.argument.class_

                self.relationships[p.key] = cls
                self.relationships_keys[p.key] = []
                for col in sqlalchemy.orm.class_mapper(cls).primary_key:
                    self.relationships_keys[p.key].append(col.name)

                if p.uselist:
                    self.collections[p.key] = cls

                else:
                    self.references[p.key] = cls

                self.references_keys[p.key] = collections.OrderedDict()
                for col in p._calculated_foreign_keys:
                    if not col.foreign_keys:
                        log.debug(dir(col.table))
                        log.debug(col.table.constraints)
                    for f in col.foreign_keys:
                        self.references_keys[p.key][col.name] = f.column.name

            else:
                msg = 'Unsupported property type: {}'.format(type(p))
                NotImplementedError(msg)

        log.debug('Fieds: %s, %s',
                  self.fields.keys(),
                  self.fields.values())
        log.debug('Relationships Keys: %s, %s',
                  self.relationships.keys(),
                  self.relationships.values())
        log.debug('Relationships: %s, %s',
                  self.relationships_keys.keys(),
                  self.relationships_keys.values())
        log.debug('References: %s, %s',
                  self.references.keys(),
                  self.references.values())
        log.debug('References Keys: %s, %s',
                  self.references_keys.keys(),
                  self.references_keys.values())
        log.debug('Collections: %s, %s',
                  self.collections.keys(),
                  self.collections.values())


class Schema(object):

    def __init__(self, entity, session=None, excludes=None):
        """ Build a Colander Schema
            based on the SQLAlchemy 'entity'.
        """
        log.debug('Create schema for: %s', entity.__name__)
        # An entity's schema has the following structure:
        # {'attr1': value1, 'attr2': value2, ...}
        self.entity = entity
        mapper = sqlalchemy.orm.class_mapper(entity)
        self.registry = Registry(mapper)
        self.session = session
        excludes = excludes if excludes else set()

        self.impl = colander.SchemaNode(colander.Mapping())
        for name, column in self.registry.fields.iteritems():
                if name in excludes:
                    continue
                node = self.get_schema_from_col(column)
                node.name = name
                self.impl.add(node)

        for name, rel in self.registry.references.iteritems():
                if name in excludes:
                    continue
                node = self.get_schema_from_rel(rel)
                node.name = name
                self.impl.add(node)

        for name, rel in self.registry.collections.iteritems():
                if name in excludes:
                    continue
                node = self.get_schema_from_rel(rel, collection=True)
                node.name = name
                self.impl.add(node)

    def get_schema_from_col(self, column):
        """ Build and return a Colander SchemaNode
            using information stored in the column.
        """

        validator = None
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

        # Add a default value for deserialized missing parameters.
        if not column.default is None:
            missing = column.default.arg

        elif column.nullable:
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
        else:
            # xToOne relationships.
            type_ = colander.Mapping()
            missing = None

        return colander.SchemaNode(type_,
                                   *nodes,
                                   missing=missing)

    def deserialize(self, data, colander_only=False):

        data = self.impl.deserialize(data)
        log.debug('Colander deserialized: %s', data)

        if colander_only:
            return data

        for name, cls in self.registry.references.iteritems():

            params = {}
            for fk, key in self.registry.references_keys[name].iteritems():
                value = data.get(fk)
                if value is None:
                    continue
                params[key] = value

            if not data[name] and not params:
                continue

            elif params:
                data[name] = params

            obj = self.deserialize_relationship(data[name], cls)

            if obj is None:
                msg = "The object in '%s' doesn't exists." % name
                raise colander.Invalid(self.impl[name],
                                       msg,
                                       value=data[name])

            data[name] = obj

        for name, cls in self.registry.collections.iteritems():

            if not data[name]:
                continue

            values = []
            for value in data[name]:

                obj = self.deserialize_relationship(value, cls)

                if obj is None:
                    msg = "The object in '%s' doesn't exists." % name
                    raise colander.Invalid(self.impl[name],
                                           msg,
                                           value=data[name])

                values.append(obj)

            data[name] = values

        return self.entity(**data)

    def deserialize_relationship(self, data, cls):
        query = self.session.query(cls)
        mapper = sqlalchemy.orm.class_mapper(cls)
        value = tuple([data[key.name] for key in mapper.primary_key])
        return query.get(value)

    def serialize(self, obj, use_colander=True):

        if not isinstance(obj, self.entity):
            msg = "Invalid object: '%s'. Only '%s' objects can be serialized."
            raise TypeError(msg % (type(obj), self.entity.__name__))

        dict_ = {}
        for name in self.registry.fields.iterkeys():
            dict_[name] = getattr(obj, name)

        for name in self.registry.references.iterkeys():
            dict_[name] = self.serialize_relationship(getattr(obj, name))

        for name in self.registry.collections.iterkeys():
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
