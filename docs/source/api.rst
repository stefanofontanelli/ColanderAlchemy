.. _api:

ColanderAlchemy API
===================

Types
~~~~~~~~~~

.. automodule:: colanderalchemy

  .. autoclass:: SQLAlchemyMapping
     :members:

     .. automethod:: __init__

        An integer representing the position of this exception's
        schema node relative to all other child nodes of this
        exception's parent schema node.  For example, if this
        exception is related to the third child node of its parent's
        schema, ``pos`` might be the integer ``3``.  ``pos`` may also
        be ``None``, in which case this exception is the root
        exception.

     .. attribute:: value

       An attribute not used internally by Colander, but which can be
       used by higher-level systems to attach arbitrary values to
       Colander exception nodes.  For example, In the system named
       Deform, which uses Colander schemas to define HTML form
       renderings, the ``value`` is used when raising an exception
       from a widget as the value which should be redisplayed when an
       error is shown.

Utilities
~~~~~~~~~~

.. automodule:: colanderalchemy

  .. autoclass:: MappingRegistry



Types
~~~~~

  .. autoclass:: Mapping
    This class is for internal use only.