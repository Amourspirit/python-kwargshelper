
ReturnTypeCheck Usage
=====================

:py:class:`~.decorator.ReturnTypeCheck` decorator reqires that return matches ``type``.

The following example requres return type of ``str`` by applying :py:class:`~.decorator.ReturnTypeCheck`
decorator with parameter of ``str``.

.. code-block:: python

    from kwhelp.decorator import ReturnTypeCheck

    @ReturnTypeCheck(str)
    def foo(*args):
        result = None
        for i, arg in enumerate(args):
            if i == 0:
                result = arg
            else:
                result = result + ", " + arg
        return result

Result when type of ``str`` is returned.

.. code-block:: python

    >>> result = foo("Hello", "World", "Happy", "Day")
    >>> print(result)
    Hello, World, Happy, Day

Error is raises when retrun type is not valid.

.. code-block:: python

    >>> result = foo(2)
    TypeError: Return Value is expected to be of 'str' but got 'int'

