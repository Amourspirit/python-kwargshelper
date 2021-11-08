AcceptedTypes Usage
===================

:py:class:`~.decorator.AcceptedTypes` Decorator that decorates methods that requires
args to match types specificed.

Includes features:

    * :doc:`/source/general/dec_feature/type_instance_check`
    * :doc:`/source/general/dec_feature/ftype`
    * :doc:`/source/general/dec_feature/opt_all_args`
    * :doc:`/source/general/dec_feature/opt_return`


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
    AcceptedTypes decorator error.

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
   AcceptedTypes decorator error.

Too many args passed into Function result in an error

.. code-block:: python

    >>> result = foo(1, 2, 3, 4, 5, 1000)
   ValueError: Invalid number of arguments for foo()
   AcceptedTypes decorator error.

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
    AcceptedTypes decorator error.

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
    AcceptedTypes decorator error.

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
    AcceptedTypes decorator error.

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
    AcceptedTypes decorator error.


Option opt_all_args
-------------------

``opt_all_args`` argument allows the last class type passed into :py:class:`~.decorator.AcceptedTypes` to
validate all remaining arguments of wrapped function.

.. code-block:: python

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

Combined Decorators
-------------------

:py:class:`~.decorator.AcceptedTypes` can be combined with other decorators.

The following example limits how many args are allowed by applying
:py:class:`~.decorator.ArgsMinMax` decorator.

.. code-block:: python

    from kwhelp.decorator import SubClass, ArgsMinMax

    @ArgsMinMax(max=6)
    @AcceptedTypes(float, (float, int), opt_all_args=True)
    def sum_num(*args):
        return sum(args)

.. code-block:: python

    >>> print(sum_num(1.3, 44.556, 10, 22, 45, 7.88))
    130.736
    >>> print(sum_num(1, 44.556, 10, 22, 45, 7.88, 100))
    ValueError: Invalid number of args pass into 'sum_num'.
    Expected max of 6. Got '7' args.
    ArgsMinMax decorator error.