# types.py
# Copyright (C) 2012 the ColanderAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of ColanderAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from collections import OrderedDict
from sqlalchemy.orm.properties import ColumnProperty
from sqlalchemy.orm.properties import RelationshipProperty
from sqlalchemy.orm import class_mapper
import sqlalchemy.schema

__all__ = ['MappingRegistry', 'Column', 'relationship']


class MappingRegistry(object):

    def __init__(self, cls, excludes=None, includes=None, nullables=None):
        """ Keep information about the SQLAlchemy mapped class `cls`.
        """
        self.cls = cls
        self._mapper = class_mapper(cls)
        self.excludes = excludes or {}
        self.includes = includes or {}
        self.nullables = nullables or {}
        self.pkeys = [col.name for col in self._mapper.primary_key]
        self.fkeys = {}
        self.rkeys = {}
        self.attrs = {}
        self.properties = {}
        self.fields = set()
        self.relationships = set()
        self.references = set()
        self.collections = set()

        for p in self._mapper.iterate_properties:

            self.properties[p.key] = p

            if isinstance(p, ColumnProperty):

                col = p.columns[0]
                self.attrs[p.key] = col
                self.fields.add(p.key)

                reg = col.ca_registry if hasattr(col, 'ca_registry') else {}
                if p.key not in self.includes and 'include' in reg:
                    self.includes[p.key] = reg['include']

                if p.key not in self.excludes and 'exclude' in reg:
                    self.excludes[p.key] = reg['exclude']

                if p.key not in self.nullables and 'nullable' in reg:
                    self.nullables[p.key] = reg['nullable']

            elif isinstance(p, RelationshipProperty):

                if callable(p.argument):
                    cls = p.argument()
                else:
                    cls = p.argument.class_

                reg = p.ca_registry if hasattr(p, 'ca_registry') else {}
                if p.key not in self.includes and 'include' in reg:
                    self.includes[p.key] = reg['include']

                if p.key not in self.excludes and 'exclude' in reg:
                    self.excludes[p.key] = reg['exclude']

                if p.key not in self.nullables and 'nullable' in reg:
                    self.nullables[p.key] = reg['nullable']

                self.attrs[p.key] = cls
                self.relationships.add(p.key)
                self.rkeys[p.key] = [col.name
                                     for col in class_mapper(cls).primary_key]
                if p.uselist:
                    self.collections.add(p.key)
                else:
                    self.references.add(p.key)
                    self.fkeys[p.key] = OrderedDict()
                    for col in p._calculated_foreign_keys:
                        if col.table in self._mapper.tables:
                            for f in col.foreign_keys:
                                self.fkeys[p.key][col.name] = f.column.name

                    if not self.fkeys[p.key]:
                        self.fkeys.pop(p.key)
            else:
                msg = 'Unsupported property type: {}'.format(type(p))
                raise NotImplementedError(msg)

            if p.key in self.includes and \
               p.key in self.excludes and \
               not self.includes[p.key] is None and \
               not self.excludes[p.key] is None and \
               self.includes[p.key] == self.excludes[p.key]:
                msg = "%s cannot be included and excluded at the same time."
                raise ValueError(msg % p.key)


class Column(sqlalchemy.schema.Column):

    def __init__(self, *args, **kwargs):

        self._ca_registry = {}
        for key in ['ca_type', 'ca_children', 'ca_name', 'ca_default',
                    'ca_missing', 'ca_preparer', 'ca_validator', 'ca_after_bind',
                    'ca_title', 'ca_description', 'ca_widget',
                    'ca_include', 'ca_exclude', 'ca_nullable']:
            try:
                value = kwargs.pop(key)

            except KeyError:
                continue

            else:
                self._ca_registry[key[3:]] = value

        super(Column, self).__init__(*args, **kwargs)

    @property
    def ca_registry(self):
        return self._ca_registry


def relationship(argument, secondary=None, **kwargs):

    registry = {}
    for key in ['ca_type', 'ca_children', 'ca_name', 'ca_default',
                'ca_missing', 'ca_preparer', 'ca_validator', 'ca_after_bind',
                'ca_title', 'ca_description', 'ca_widget',
                'ca_include', 'ca_exclude', 'ca_nullable']:
        try:
            value = kwargs.pop(key)

        except KeyError:
            continue

        else:
            registry[key[3:]] = value

    relationship = sqlalchemy.orm.relationship(argument, secondary, **kwargs)
    relationship.ca_registry = registry
    return relationship
