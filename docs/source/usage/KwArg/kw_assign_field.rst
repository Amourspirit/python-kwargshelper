Kw_assign field
===============

Field value can be assigned by adding ``field`` arg to :py:meth:`~.KwArg.kw_assign` method.
Sometimes it may be necessary to pass an arg with a name but change it in :py:class:`~.KwArg` instance.

In the following ``is_key_existing`` is assigned to ``is_key_exist`` of :py:class:`~.KwArg` instance.
This avoids a :py:class:`.ReservedAttributeError` because ``is_key_existing`` is a reserved keyword of :py:class:`~.KwArg`.

.. code-block:: python

    def is_key(**kwargs) -> str:
        keys = ('one','two', 'four', 'eight')
        kw = KwArg(**kwargs)
        kw.kw_assign(key='is_key_existing', field='is_key_exist', require=True, types=[str])
        if kw.is_key_exist in keys:
            return True
        return False


.. code-block:: python

    >>> result = is_key(is_key_existing="one")
    >>> print(result)
    True
    >>> result = is_key(is_key_existing="three")
    >>> print(result)
    False
