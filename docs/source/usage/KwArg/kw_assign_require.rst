Kw_assign Require Arg
=====================

Values can be required by adding ``require`` args to :py:meth:`~.KwArg.kw_assign` method.

In the following ``first`` and ``second`` args are required

.. include:: /source/inc/ex/KwArg_basic.rst

``first`` and ``second`` are required. ``msg`` is not required and has a default value.
``end`` is not required.

.. code-block:: python

    >>> result = my_method(first=10, second=22)
    >>> print(result)
    Result: 32

Output when optional ``args`` end and ``msg`` are included.

.. code-block:: python

    >>> result = my_method(first=10, second=22, end="!", msg="Tally")
    >>> print(result)
    Tally 32!

Method will raise an error as ``msg`` must be of type ``str`` as defined by ``types``

.. code-block:: python

    >>> result = result= my_method(first=10)
    ValueError: KwArg arg 'second' is required