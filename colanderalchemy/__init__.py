# __init__.py
# Copyright (C) 2012 the ColanderAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of ColanderAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from .schema import SQLAlchemySchemaNode

__all__ = ['SQLAlchemySchemaNode']


__colanderalchemy__ = '__colanderalchemy__'


def setup_schema(mapper, class_):
    setattr(class_, __colanderalchemy__, SQLAlchemySchemaNode(class_))
