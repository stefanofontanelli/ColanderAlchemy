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
    """ Build a Colander schema for ``class_`` and attach it to that class.

    This method is designed to be attached to the ``mapper_configured``
    event from SQLAlchemy.

    See http://docs.sqlalchemy.org/en/latest/orm/events.html#sqlalchemy.orm.events.MapperEvents.mapper_configured for more information about event handling.

    Arguments/Keywords

    mapper
        The mapper associated with the given ``class_``.  This is typically
        passed automatically via the SQLAlchemy event handler.

        May be specified as ``None`` if this method is being called manually.

    class\_
        The SQLAlchemy mapped class. This class may have
        attributes, related mapped classes (via SQLAlchemy relationships)
        and the like.
    """
    setattr(class_, __colanderalchemy__, SQLAlchemySchemaNode(class_))
