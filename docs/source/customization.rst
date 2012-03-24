.. _customization:

Change autogeneration rules
===========================

Default Colander schema generated using SQLAlchemyMapping follows the rules below:
    1) it has a not required field for each not required column and for each relationship,
    2) it has a required field for each primary key or not nullable column,
    3) it has a default field for each column which has a default value,
    4) it validates ``Enum`` columns using Colander ``OneOf`` validator.

The user can change default behaviour specifing keyword arguments 
``excludes`` and/or ``nullables``::

    from colanderalchemy import SQLAlchemyMapping


    schema = SQLAlchemyMapping(Account,
                               excludes=('age', 'gender'),
                               nullables={'surname'=True})

    data = {
        "name": "colander",
        "surname": "alchemy",
        "email": "mailbox@domain.tld",
        "gender": "M",
        "age": "30"
    }
    deserialized = schema.deserialize(data)
    serialized = schema.serialize(deserialized)
