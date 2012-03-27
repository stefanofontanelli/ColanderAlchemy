# types.py
# Copyright (C) 2012 the ColanderAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of ColanderAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from collections import OrderedDict
from logging import getLogger
from sqlalchemy.orm.properties import ColumnProperty
from sqlalchemy.orm.properties import RelationshipProperty
from sqlalchemy.orm import class_mapper

__all__ = ['MappingRegistry']


class MappingRegistry(object):

    def __init__(self, cls, excludes=None, includes=None, nullables=None):
        """ Keep information about the SQLAlchemy mapped class `cls`.
        """
        self.cls = cls
        self._mapper = class_mapper(cls)
        self.excludes = excludes or set()
        self.includes = includes or set()
        self.nullables = nullables or {}
        self.pkeys = [col.name for col in self._mapper.primary_key]
        self.fkeys = {}
        self.rkeys = {}
        self.attrs = {}
        self.fields = set()
        self.relationships = set()
        self.references = set()
        self.collections = set()

        if self.includes and self.excludes:
            raise ValueError('includes and excludes parameters are exclusive, specify only one of them')

        for p in self._mapper.iterate_properties:
            if isinstance(p, ColumnProperty):
                self.attrs[p.key] = p.columns[0]
                self.fields.add(p.key)

            elif isinstance(p, RelationshipProperty):

                if callable(p.argument):
                    cls = p.argument()
                else:
                    cls = p.argument.class_

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

        self._log = getLogger(__name__)
        self._log.debug('Registry created.')
        self._log.debug('Keys: %s', self.pkeys)
        self._log.debug('Foreign Keys: %s', self.fkeys)
        self._log.debug('Fieds: %s', self.fields)
        self._log.debug('Relationships: %s', self.relationships)
        self._log.debug('Relationships Keys: %s, %s',
                        self.rkeys.keys(), self.rkeys.values())
        self._log.debug('References: %s', self.references)
        self._log.debug('Collections: %s', self.collections)
