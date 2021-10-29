AcceptedTypes Usage
===================

:py:class:`~.decorator.AcceptedTypes` Decorator that decorates methods that requires
args to match types specificed.

Normal Function
---------------

The following example requres:

    * ``one`` is of type ``int``
    * ``two`` is of type ``float`` or ``int``
    * ``three`` is of type ``str``.
  
.. code-block:: python

    from kwhelp.decorator import AcceptedTypes

    @AcceptedTypes(int, (float, int), str)
    def foo(one, two, three):
        result = [one, two, three]
        return result

.. code-block:: python

    >>> result = foo(1, 2.2, "Hello")
    >>> print(result)
    [1, 2.2, 'Hello'] 


.. code-block:: python

    >>> result = foo(1, 2.2, "Hello")
    >>> print(result)
    TypeError: Arg 'two' is expected to be of '<class 'float'> | <class 'int'>' but got 'str'

``*args``
+++++++++

``*args`` can be used a parameters. When using ``*args`` with :py:class:`~.decorator.AcceptedTypes` the
total number of args for the function must match the number of types passed into ``AcceptedTypes``.

.. code-block:: python

    from kwhelp.decorator import AcceptedTypes

    @AcceptedTypes(int, (float, int), int, (int, str), int)
    def foo(one, two, three, *args):
        result = [one, two, three]
        for arg in args:
            result.append(arg)
        return result

All value of type ``int``

.. code-block:: python

    >>> result = foo(1, 2, 3, 4, 5)
    >>> print(result)
    [1, 2, 3, 4, 5]

Alternative type for args that support them.

.. code-block:: python

    >>> result = foo(1, 2.77, 3, "Red", 5)
    >>> print(result)
    [1, 2.77, 3, 'Red', 5]

Last arg is not of type ``int`` and raised an error

.. code-block:: python

    >>> result = foo(1, 2, 3, 4, 5.766)
   TypeError: Arg Value is expected to be of '<class 'int'>' but got 'float'

Too many args passed into Function result in an error

.. code-block:: python

    >>> result = foo(1, 2, 3, 4, 5, 1000)
   ValueError: Invalid number of arguments for foo()

``**kwargs``
++++++++++++

``**kwargs`` can be used a parameters. When using ``*args`` with :py:class:`~.decorator.AcceptedTypes` the
total number of args for the function must match the number of types passed into ``AcceptedTypes``.

.. code-block:: python

    @AcceptedTypes(int, (float, int), int, (int, str), int)
    def foo(one, *args, **kwargs):
        result_args = [*args]
        result_args.insert(0, one)
        result_dic = {**kwargs}
        return result_args, result_dic

All ``int`` values with last arg as key, value.

.. code-block:: python

    >>> result = foo(1, 2, 3, 4, last=5)
    >>> print(result)
    ([1, 2, 3, 4], {'last': 5})

.. code-block:: python

    >>> result = foo(1, 2, 3, 4, last=5, exceeded=None)
    ValueError: Invalid number of arguments for foo()

Class Method
------------

:py:class:`~.decorator.AcceptedTypes` can be applied to class methods.
When appling to class method set the ``ftype`` arg to match :py:class:`~.decorator.DecFuncEnum`.

Regular Class Method
++++++++++++++++++++

Class method applying to constructor.

.. code-block:: python

    from kwhelp.decorator import AcceptedTypes, DecFuncEnum

    class Foo:
        @AcceptedTypes((int, float), (int, float), ftype=DecFuncEnum.METHOD)
        def __init__(self, start, stop):
            self.start = start
            self.stop = stop


.. code-block:: python

    >>> f = Foo(1, 99.9)
    >>> print(f.start, f.stop)
    1 99.9

.. code-block:: python

    >>> f = Foo(1, None)
    TypeError: Arg 'stop' is expected to be of '<class 'int'> | <class 'float'>' but got 'NoneType'

Static Class Method
+++++++++++++++++++

:py:class:`~.decorator.AcceptedTypes` can be use on static method of a class as well by
setting ``ftype`` to :py:class:`~.decorator.DecFuncEnum` ``METHOD_STATIC`` option.

.. code-block:: python

    from kwhelp.decorator import AcceptedTypes, DecFuncEnum, ReturnType

    class Foo:
        @staticmethod
        @AcceptedTypes(int, int, ftype=DecFuncEnum.METHOD_STATIC)
        @ReturnType(int)
        def add(first, last):
            return first + last

.. code-block:: python

    >>> print(Foo.add(34, 76))
    110

.. code-block:: python

    >>> print(Foo.add(7.2, 76))
    TypeError: Arg 'first' is expected to be of '<class 'int'>' but got 'float'

Class Method
++++++++++++

:py:class:`~.decorator.AcceptedTypes` can be use on class method of a class as well by
setting ``ftype`` to :py:class:`~.decorator.DecFuncEnum` ``METHOD_CLASS`` option.

.. code-block:: python

    from kwhelp.decorator import AcceptedTypes, DecFuncEnum, ReturnType

    class Foo:
        @classmethod
        @AcceptedTypes(int, int, ftype=DecFuncEnum.METHOD_CLASS)
        @ReturnType(int)
        def add(cls, first, last):
            return first + last

.. code-block:: python

    >>> print(Foo.add(34, 76))
    110

.. code-block:: python

    >>> print(Foo.add(7.2, 76))
    TypeError: Arg 'first' is expected to be of '<class 'int'>' but got 'float'