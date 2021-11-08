ReturnType Usage
================

:py:class:`~.decorator.ReturnType` decorator reqires that return matches ``type``.

Includes features:

    * :doc:`/source/general/dec_feature/type_instance_check`
    * :doc:`/source/general/dec_feature/opt_return`

Single Arg Usage
----------------

The following example requres return type of ``str`` by applying :py:class:`~.decorator.ReturnType`
decorator with parameter of ``str``.

.. code-block:: python

    from kwhelp.decorator import ReturnType

    @ReturnType(str)
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
    TypeError: Return Value is expected to be of '<class 'str'>' but got 'int'.
    ReturnType decorator error.

Multiple Arg Usage
------------------

:py:class:`~.decorator.ReturnType` can accept multiple return types.

In the following example return type must be ``int`` or ``str``.

.. code-block:: python

    from kwhelp.decorator import ReturnType

    @ReturnType(int, str)
    def ret_test(start, length, end):
        result = start + length + end
        return result

.. code-block:: python

    >>> result = ret_test(2, 4, 6)
    >>> print(result)
    12

.. code-block:: python

    >>> result = ret_test("In the beginning ", "and forever more, ", "time is everlasting.")
    >>> print(result)
    In the beginning and forever more, time is everlasting.

.. code-block:: python

    >>> result = ret_test(1.33, 4, 6)
    TypeError: Return Value is expected to be of '<class 'int'> | <class 'str'>' but got 'float'