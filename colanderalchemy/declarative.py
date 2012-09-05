# declarative.py
# Copyright (C) 2012 the ColanderAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of ColanderAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

import sqlalchemy.schema
import sqlalchemy.ext.declarative

__all__ = ['Column', 'relationship']


class Column(sqlalchemy.schema.Column):

    def __init__(self, *args, **kwargs):

        self._ca_registry = {}
        for key in ['ca_type', 'ca_children', 'ca_default',
                    'ca_missing', 'ca_preparer', 'ca_validator',
                    'ca_after_bind', 'ca_title', 'ca_description',
                    'ca_widget', 'ca_include', 'ca_exclude', 'ca_nullable',
                    'ca_order']:
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

    def copy(self, **kwargs):
        col = super(Column, self).copy(**kwargs)
        col._ca_registry = self._ca_registry.copy()
        return col


def relationship(argument, secondary=None, **kwargs):

    registry = {}
    for key in ['ca_type', 'ca_children', 'ca_default',
                'ca_missing', 'ca_preparer', 'ca_validator', 'ca_after_bind',
                'ca_title', 'ca_description', 'ca_widget',
                'ca_include', 'ca_exclude', 'ca_nullable', 'ca_order']:
        try:
            value = kwargs.pop(key)

        except KeyError:
            continue

        else:
            registry[key[3:]] = value

    relationship = sqlalchemy.orm.relationship(argument, secondary, **kwargs)
    relationship.ca_registry = registry
    return relationship
