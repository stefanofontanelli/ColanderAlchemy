.. ColanderAlchemy documentation master file, created by
   sphinx-quickstart on Wed Mar  7 18:12:21 2012.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

ColanderAlchemy
===============

ColanderAlchemy is a library for automatic creation of a 
`Colander <http://http://docs.pylonsproject.org/projects/colander/en/latest/>`_ 
schema based on a `SQLAlchemy <http://www.sqlalchemy.org/>`_ mapped object.

Use of ColanderAlchemy is really simple.
Suppose you have an SQLAlchemy mapped class like the one described below::

    from sqlalchemy import Column
    from sqlalchemy import Enum
    from sqlalchemy import Integer
    from sqlalchemy import Unicode
    from sqlalchemy.ext.declarative import declarative_base


    Base = declarative_base()


    class Account(Base):

        __tablename__ = 'accounts'

        email = Column(Unicode(256), primary_key=True)
        name = Column(Unicode(128), nullable=False)
        surname = Column(Unicode(128), nullable=False)
        gender = Column(Enum(u'M', u'F'))
        age = Column(Integer)


The code that you need to get a Colander schema based on
``Account`` mapped class is::

    from colanderalchemy import BaseSchema

    data = {
        "name": "colander",
        "surname": "alchemy",
        "email": "mailbox@domain.tld",
        "gender": "M",
        "age": "30"
    }
    schema = BaseSchema(Account)
    deserialized = schema.deserialize(data)
    serialized = schema.serialize(deserialized)

The ``deserialized`` variable will be::

    {
        "name": "colander",
        "surname': "alchemy",
        "email': "mailbox@domain.tld",
        "gender': "M",
        "age": 30
    }

The ``serialized`` variable will be equal to ``data``::

    {
        "name": "colander",
        "surname': "alchemy",
        "email': "mailbox@domain.tld",
        "gender': "M",
        "age": "30"
    }

Note that the behaviors of ``schema.deserialize`` and ``schema.serialize``
are the same as that of Colander ones.




Contents:

.. toctree::
   :maxdepth: 2

    api.rst


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

