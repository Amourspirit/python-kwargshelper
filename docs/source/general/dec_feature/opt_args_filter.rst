opt_args_filter
===============

``opt_args_filter``  allows decorators that support it filter which type of argument will be validated.

The following example is with :py:class:`~.decorator.AcceptedTypes` but is similar for all decorators that
support ``opt_args_filter`` option.

ARGS
----

``DecArgEnum.ARGS`` filter. Only ``*args`` are validated.

.. code-block:: python

    from kwhelp.decorator import AcceptedTypes, DecArgEnum

    @AcceptedTypes(int, opt_all_args=True, opt_args_filter=DecArgEnum.ARGS)
    def foo(*args, first, last, **kwargs):
        return [*args] + [first, last] + [v for _, v in kwargs.items()]

.. code-block:: python

    >>> result = foo(1, 2, 3, 4, 5, 6, first="one", one="1st", two="2nd", third="3rd")
    >>> print(result)
    [1, 2, 3, 4, 5, 6, 'one', '!!!', '1st', '2nd', '3rd']
    >>> foo(1, 45.66, 3, 4, 5, 6, first="one", one="1st", two="2nd", third="3rd")
    TypeError: Arg in 2nd position of is expected to be of 'int' but got 'float'.
    AcceptedTypes decorator error.

NAMED_ARGS
----------

``DecArgEnum.NAMED_ARGS`` filter. Only named args are validated. ``*args`` and ``**kwargs`` are excluded.

.. code-block:: python

    from kwhelp.decorator import AcceptedTypes, DecArgEnum

    @AcceptedTypes(int, int, opt_args_filter=DecArgEnum.NAMED_ARGS)
    def foo(*args, first, last, **kwargs):
        return [*args] + [first, last] + [v for _, v in kwargs.items()]

.. code-block:: python

    >>> result = foo("a", "b", "c", first=1, last= 3, one="1st", two="2nd", third="3rd")
    >>> print(result)
    ['a', 'b', 'c', 1, 3, '1st', '2nd', '3rd']
    >>> result = foo("a", "b", "c", first=1.5, last=3, one="1st", two="2nd", third="3rd")
    TypeError: Arg 'first' in 1st position is expected to be of 'int' but got 'float'.
    AcceptedTypes decorator error.

KWARGS
------

``DecArgEnum.KWARGS`` filter. Only ``**kwargs`` are validated. ``*args`` and named args are excluded.

.. code-block:: python

    from kwhelp.decorator import AcceptedTypes, DecArgEnum

    @AcceptedTypes((int, float), opt_all_args=True, opt_args_filter=DecArgEnum.KWARGS)
    def foo(*args, first, last="!", **kwargs):
        return [*args] + [first, last] + [v for _, v in kwargs.items()]

.. code-block:: python

    >>> result = foo("a", "b", "c", first=-100, one=101, two=2.2, third=33.33)
    >>> print(result)
    ['a', 'b', 'c', -100, '!', 101, 2.2, 33.33]
    >>> result = foo("a", "b", "c", first=-100, one=101, two="two", third=33.33)
    TypeError: Arg 'two' in 2nd position is expected to be of 'float' or 'int' but got 'str'.
    AcceptedTypes decorator error.

NO_ARGS
-------

``DecArgEnum.NO_ARGS`` filter. Only all args except for ``*args``.

.. code-block:: python

    from kwhelp.decorator import AcceptedTypes, DecArgEnum

    @AcceptedTypes((int, float), opt_all_args=True, opt_args_filter=DecArgEnum.NO_ARGS)
    def foo(*args, first, last=1001, **kwargs):
        return [*args] + [first, last] + [v for _, v in kwargs.items()]

.. code-block:: python

    >>> result = foo("a", "b", "c", first=-100, one=101, two=22.22, third=33.33)
    >>> print(result)
    ['a', 'b', 'c', -100, 1001, 101, 22.22, 33.33]
    >>> result = foo("a", "b", "c", first=-100, one="1st", two=22.22, third=33.33)
    TypeError: Arg 'one' in 3rd position is expected to be of 'float' or 'int' but got 'str'.
    AcceptedTypes decorator error
    >>> result = foo("a", "b", "c", first=-100, one=101.11, two="2nd", third=33.33)
    TypeError: Arg 'two' in 4th position is expected to be of 'float' or 'int' but got 'str'.
    AcceptedTypes decorator error.
