# types.py
# Copyright (C) 2012 the ColanderAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of ColanderAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from sqlalchemy.orm import class_mapper
from utils import MappingRegistry
import colander
import sqlalchemy.types

__all__ = ['SQLAlchemyMapping']


class SQLAlchemyMapping(colander.SchemaNode):

    def __init__(self, cls, excludes=None, nullables=None, unknown='raise'):
        """ Build a Colander Schema based on the SQLAlchemy mapped class.
        """
        super(SQLAlchemyMapping, self).__init__(colander.Mapping())
        self._reg = MappingRegistry(cls, excludes, nullables)
        for name, obj in self._reg.attrs.iteritems():

            if name in self._reg.excludes:
                continue

            elif name in self._reg.fields:
                node = self.get_schema_from_col(obj,
                                                self._reg.nullables.get(name))

            else:
                node = self.get_schema_from_rel(obj,
                                                name in self._reg.collections)
            node.name = name
            self.add(node)

    def get_schema_from_col(self, column, nullable=None):
        """ Build and return a Colander SchemaNode
            using information stored in the column.
        """

        validator = None
        # Add a default value for missing parameters during serialization.
        default = None if column.default is None else column.default.arg
        # Add a default value for  missing parameters during deserialization.
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
            raise NotImplementedError('Unknown type: %s' % column.type)

        # Overwrite default missing value when nullable is specified.
        if nullable == False:
            missing = colander.required

        elif nullable == True:
            missing = None

        if default is None:
            default = colander.null

        return colander.SchemaNode(type_,
                                   name=column.name,
                                   validator=validator,
                                   missing=missing,
                                   default=default)

    def get_schema_from_rel(self, cls, uselist=False, nullable=None):
        """ Build and return a Colander SchemaNode
            using information stored in the relationship property.
        """

        mapper = class_mapper(cls)
        nodes = [self.get_schema_from_col(col) for col in mapper.primary_key]

        if uselist:
            # xToMany relationships.
            type_ = colander.Sequence()
            missing = []
        else:
            # xToOne relationships.
            type_ = colander.Mapping()
            missing = None

        if nullable == False:
            missing = colander.required

        default = colander.null

        return colander.SchemaNode(type_,
                                   *nodes,
                                   missing=missing,
                                   default=default)
