opt_all_args
============

``opt_all_args`` argument allows the last paramater passed into ``*args`` to
validate all remaining arguments of wrapped function.

.. code-block:: python

    from kwhelp.decorator import AcceptedTypes

    @AcceptedTypes(float, (float, int), opt_all_args=True)
    def sum_num(*args):
        return sum(args)

The first arg of ``sum_num`` must be a ``float``. Remaining args can be ``float`` or ``int``.

.. code-block:: python

    >>> print(sum_num(1.3, 44.556, 10, 22, 45, 7.88))
    130.736
    >>> print(sum_num(1, 44.556, 10, 22, 45, 7.88))
    TypeError: Arg in 1st position of is expected to be of '<class 'float'>' but got 'int'
    AcceptedTypes decorator error.
    >>> print(sum_num(1.3, 44.556, 10, 22, 45, 7.88, "77"))
    TypeError: Arg in 3rd position of is expected to be of '(<class 'float'>, <class 'int'>)' but got 'str'
    AcceptedTypes decorator error.