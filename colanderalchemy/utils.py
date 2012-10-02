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
        self.excludes = excludes or {}
        self.includes = includes or {}
        self.nullables = nullables or {}
        self.pkeys = []
        self.fkeys = OrderedDict()
        self.rkeys = OrderedDict()
        self.attrs = OrderedDict()
        self.properties = OrderedDict()
        self.fields = set()
        self.relationships = set()
        self.references = set()
        self.collections = set()
        self.ordering = OrderedDict()

        counter = 0
        for p in self._mapper.iterate_properties:

            self.properties[p.key] = p

            if isinstance(p, ColumnProperty):

                col = p.columns[0]
                self.attrs[p.key] = col
                self.fields.add(p.key)
                if col.foreign_keys:
                    self.fkeys[p.key] = p

                if col in self._mapper.primary_key:
                    self.pkeys.append(p.key)

                reg = col.ca_registry.copy() if hasattr(col, 'ca_registry') else {}
                if p.key not in self.includes and\
                   'include' in reg and reg['include']:
                    self.includes[p.key] = reg['include']

                if p.key not in self.excludes and 'exclude' in reg:  # and reg['exclude']:
                    self.excludes[p.key] = reg['exclude']

                if p.key not in self.nullables and 'nullable' in reg:
                    self.nullables[p.key] = reg['nullable']

                self.ordering[reg.get('order', counter)] = p.key

            elif isinstance(p, RelationshipProperty):

                if callable(p.argument):
                    cls = p.argument()
                else:
                    cls = p.argument.class_

                reg = p.ca_registry if hasattr(p, 'ca_registry') else {}
                if p.key not in self.includes and\
                   'include' in reg and reg['include']:
                    self.includes[p.key] = reg['include']

                if p.key not in self.excludes and\
                   'exclude' in reg and reg['exclude']:
                    self.excludes[p.key] = reg['exclude']

                if p.key not in self.nullables and 'nullable' in reg:
                    self.nullables[p.key] = reg['nullable']

                self.attrs[p.key] = cls
                self.relationships.add(p.key)
                self.ordering[reg.get('order', counter)] = p.key
                self.rkeys[p.key] = [col.name
                                     for col in class_mapper(cls).primary_key]
                if p.uselist:
                    self.collections.add(p.key)
                else:
                    self.references.add(p.key)
                    # Check need of code below.
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

            counter += 1

            if p.key in self.includes and \
               p.key in self.excludes and \
               not self.includes[p.key] is None and \
               not self.excludes[p.key] is None and \
               self.includes[p.key] == self.excludes[p.key]:
                msg = "%s cannot be included and excluded at the same time."
                raise ValueError(msg % p.key)
