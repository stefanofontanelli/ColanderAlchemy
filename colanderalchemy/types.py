# types.py
# Copyright (C) 2012 the ColanderAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of ColanderAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php
try:
    from collections import OrderedDict

except ImportError:
    from backports import OrderedDict

from sqlalchemy.orm import class_mapper
from sqlalchemy.orm import object_mapper
from .utils import MappingRegistry
import colander
import sqlalchemy.types

__all__ = ['SQLAlchemyMapping']


class SQLAlchemyMapping(colander.SchemaNode):

    def __init__(self, cls, excludes=None,
                 includes=None, nullables=None, unknown='raise'):
        """ Build a Colander Schema based on the SQLAlchemy mapped class.
        """
        super(SQLAlchemyMapping, self).__init__(colander.Mapping(unknown))

        self._reg = MappingRegistry(cls, excludes, includes, nullables)
        for i in sorted(self._reg.ordering):

            name = self._reg.ordering[i]
            obj = self._reg.attrs[name]

            if name in self._reg.excludes and self._reg.excludes[name]:
                continue

            if self._reg.includes and name not in self._reg.includes:
                continue

            if name in self._reg.fields:
                node = self.get_schema_from_col(obj,
                                                name,
                                                self._reg.nullables.get(name))

            else:
                node = self.get_schema_from_rel(obj,
                                                name,
                                                name in self._reg.collections)
            self.add(node)

    @property
    def registry(self):
        return self._reg

    def get_schema_from_col(self, column, name, nullable=None):
        """ Build and return a Colander SchemaNode
            using information stored in the column.
        """

        if hasattr(column, 'ca_registry'):
            params = column.ca_registry.copy()

        else:
            params = {}

        # support sqlalchemy.types.TypeDecorator
        column_type = getattr(column.type, 'impl', column.type)

        if 'type' in params:
            type_ = params.pop('type')

        elif isinstance(column_type, sqlalchemy.types.Boolean):
            type_ = colander.Boolean()

        elif isinstance(column_type, sqlalchemy.types.Date):
            type_ = colander.Date()

        elif isinstance(column_type, sqlalchemy.types.DateTime):
            type_ = colander.DateTime()

        elif isinstance(column_type, sqlalchemy.types.Enum):
            type_ = colander.String()

        elif isinstance(column_type, sqlalchemy.types.Float):
            type_ = colander.Float()

        elif isinstance(column_type, sqlalchemy.types.Integer):
            type_ = colander.Integer()

        elif isinstance(column_type, sqlalchemy.types.String):
            type_ = colander.String()

        elif isinstance(column_type, sqlalchemy.types.Numeric):
            type_ = colander.Decimal()

        elif isinstance(column_type, sqlalchemy.types.Time):
            type_ = colander.Time()

        else:
            raise NotImplementedError('Unknown type: %s' % column.type)

        if 'children' in params:
            children = params.pop('children')
        else:
            children = []

        # Add a default value for missing parameters during serialization.
        if 'default' not in params and column.default is None:
            params['default'] = colander.null

        elif 'default' not in params and not column.default is None:
            if column.default.is_callable:
                # Fix: SQLA wraps callables in lambda ctx: fn().
                default = column.default.arg(None)
            else:
                default = column.default.arg
            params['default'] = default

        # Add a default value for  missing parameters during deserialization.
        if 'missing' not in params and not column.nullable:
            params['missing'] = colander.required

        elif 'missing' not in params and column.default is None:
            params['missing'] = None

        elif 'missing' not in params and not column.default is None:
            if column.default.is_callable:
                # Fix: SQLA wraps default callables in lambda ctx: fn().
                default = column.default.arg(None)
            else:
                default = column.default.arg
            params['missing'] = default

        # Overwrite default missing value when nullable is specified.
        if nullable is False:
            params['missing'] = colander.required

        elif nullable is True:
            params['missing'] = None

        if 'validator' not in params and \
           isinstance(column_type, sqlalchemy.types.Enum):

            params['validator'] = colander.OneOf(column.type.enums)

        elif 'validator' not in params and \
           isinstance(column_type, sqlalchemy.types.Enum):

            params['validator'] = colander.Length(0, column.type.length)

        # The name of SchemaNode must be the same of SQLA class attribute.
        params['name'] = name

        return colander.SchemaNode(type_, *children, **params)

    def get_schema_from_rel(self, cls, name, uselist=False, nullable=None):
        """ Build and return a Colander SchemaNode
            using information stored in the relationship property.
        """

        if hasattr(self._reg.properties[name], 'ca_registry'):
            params = self._reg.properties[name].ca_registry.copy()

        else:
            params = {}

        # The name of SchemaNode must be the same of SQLA class attribute.
        params['name'] = name

        if 'type' in params:
            type_ = params.pop('type')

        elif uselist:
            # xToMany relationships.
            type_ = colander.Sequence()

        else:
            # xToOne relationships.
            type_ = colander.Mapping()

        if 'children' in params:
            children = params.pop('children')

        else:
            mapper = class_mapper(cls)
            children = [self.get_schema_from_col(col, col.name)
                        for col in mapper.primary_key]

        if nullable == False:
            params['missing'] = colander.required

        elif 'type' not in params and uselist:
            params['missing'] = []

        elif 'type' not in params:
            params['missing'] = None

        if 'default' not in params:
            params['default'] = colander.null

        return colander.SchemaNode(type_, *children, **params)

    def dictify(self, obj):
        """ Build and return a dictified version of `obj`
            using schema information to choose what attributes
            will be included in the returned dict.
        """

        dict_ = OrderedDict()
        for name in self._reg.attrs:

            if (name in self._reg.excludes and self._reg.excludes[name]) or\
               (self._reg.includes and name not in self._reg.includes):
                continue

            if name in self._reg.fields:
                dict_[name] = getattr(obj, name)

            elif name in self._reg.references:
                value = getattr(obj, name)
                if not value is None:
                    value = self.dictify_relationship(value)
                dict_[name] = value

            elif name in self._reg.collections:
                dict_[name] = [self.dictify_relationship(value)
                               for value in getattr(obj, name)]

        return dict_

    def dictify_relationship(self, obj):
        dict_ = {}
        for col in object_mapper(obj).primary_key:
            dict_[col.name] = getattr(obj, col.name)
        return dict_

    def clone(self):
        cloned = self.__class__(self._reg.cls,
                                self._reg.excludes,
                                self._reg.includes,
                                self._reg.nullables)
        cloned.__dict__.update(self.__dict__)
        cloned.children = [node.clone() for node in self.children]
        return cloned
