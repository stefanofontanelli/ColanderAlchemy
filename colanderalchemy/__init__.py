# __init__.py
# Copyright (C) 2012 the ColanderAlchemy authors and contributors
# <see AUTHORS file>
#
# This module is part of ColanderAlchemy and is released under
# the MIT License: http://www.opensource.org/licenses/mit-license.php

from .schema import SQLAlchemySchemaNode

__all__ = ['SQLAlchemySchemaNode']


__colanderalchemy__ = '__colanderalchemy__'


def setup_schema(class_):
    """ Build a Colander schema for ``class_`` and attach it to that class.

    Configuration for the resulting Colander schema can be customised by
    using either ``info`` against columns or relationships, or
    ``__colanderalchemy_config__`` against individual mapped classes.
    
    Arguments/Keywords

    class\_
        A pre-existing SQLAlchemy mapped class. This class may have
        attributes, related mapped classes (via SQLAlchemy relationships)
        and the like.
    """
    setattr(class_, __colanderalchemy__, SQLAlchemySchemaNode(class_))
