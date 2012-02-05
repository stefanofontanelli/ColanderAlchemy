#!/usr/bin/env python
# -*- coding: utf-8 -*-

import colander
import sqlalchemy.orm
import sqlalchemy.orm.properties
import sqlalchemy.types

def get_schema_from_column(property_, registry):
    """ Build and return a Colander SchemaNode
        using information stored in the column property.
    """

    column = property_.columns[0]
    validator = None
    missing = colander.required

    if column.primary_key:
        registry['id'] = property_.key

    registry['fields'].append(property_.key)

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
                               name=property_.key,
                               validator=validator,
                               missing=missing)

def get_schema_from_relationship(property_,
                                 registry,
                                 get_schema_from_column=get_schema_from_column):
    """ Build and return a Colander SchemaNode
        using information stored in the relationship property.
    """

    if callable(property_.argument):
        cls = property_.argument()

    else:
        cls = property_.argument.class_

    mapper = sqlalchemy.orm.class_mapper(cls)
    prop = mapper.get_property_by_column(mapper.primary_key[0])

    node = get_schema_from_column(prop)

    if property_.uselist:
        # xToMany relationships.
        node = colander.SchemaNode(colander.Sequence(),
                                   node,
                                   name=property_.key,
                                   missing=[])
        registry['relationships']['many'][property_.key] = cls
    else:
        # xToOne relationships.
        node.name = property_.key
        node.missing = None
        registry['relationships']['one'][property_.key] = cls

    return node

def get_schema(entity,
               get_schema_from_column=get_schema_from_column,
               get_schema_from_relationship=get_schema_from_relationship):

    # An entity's schema has the following structure:
    # {'attr1': value1, 'attr2': value2, ...}
    schema = colander.SchemaNode(colander.Mapping())
    registry = {
        'id': None, # The name of the field used to identify the entity.
        'fields': [],
        'relationships': {
            'one': {},
            'many': {},
        },
    }

    mapper = sqlalchemy.orm.class_mapper(entity)

    if len(mapper.primary_key) > 1:
        raise NotImplemented('Composite primary keys are not supported.')

    for prop in mapper.iterate_properties:

        if isinstance(prop, sqlalchemy.orm.properties.ColumnProperty):

            node = get_schema_from_column(prop, registry)

        elif isinstance(prop, sqlalchemy.orm.properties.RelationshipProperty):

            node = get_schema_from_relationship(prop, get_schema_from_column)

        else:
            NotImplemented('Unsupported property type: %s' % prop)

        schema.add(node)

    setattr(schema, '__colanderalchemy__', registry)
    return schema

def get_registry(schema):
    return getattr(schema, '__colanderalchemy__')
