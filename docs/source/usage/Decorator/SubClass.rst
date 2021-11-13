SubClass Usage
===============

:py:class:`~.decorator.SubClass` decorator that requires args of a function to match
or be a subclass of types specificed in constructor.

Includes features:

    * :doc:`/source/general/dec_feature/ftype`
    * :doc:`/source/general/dec_feature/opt_all_args`
    * :doc:`/source/general/dec_feature/opt_args_filter`
    * :doc:`/source/general/dec_feature/opt_return`
    * :doc:`/source/general/dec_feature/raise_error`

Sample Classes

.. code-block:: python
    
    from enum import IntEnum, auto

    class Color(IntEnum):
        RED = auto()
        GREEN = auto()
        BLUE = auto()

        def __str__(self) -> str:
            return self._name_

    class Base:
        def __str__(self) -> str:
            return self.__class__.__name__
    class Obj:
        def __str__(self) -> str:
            return self.__class__.__name__
    class Foo(Base): pass
    class Bar(Foo): pass
    class FooBar(Bar): pass
    class ObjFoo(Obj): pass

Decorating with ``*args``
-------------------------

Single arg match
++++++++++++++++

This example requires that all args positive ``Foo`` or positive ``ObjFoo``.
Each subclass type in ``SubClass`` constructor represents one positional arg.
In the following example two postional args are expected.

.. code-block:: python

    from kwhelp.decorator import SubClass

    @SubClass(Foo, ObjFoo)
    def do_something(*args):
        return [str(arg) for arg in args]

Expected args pass validatation.

.. code-block:: python

    >>> print(do_something(Foo(), ObjFoo()))
        ['Foo', 'ObjFoo']

Types dictate that if first arg is not a subclass of ``Foo`` or
first arg is not a subclass of ``ObjFoo`` then an error will be raised.

.. code-block:: python

    >>> print(do_something(Foo(), Obj()))
    TypeError: Arg in 2nd position is expected to be of a subclass of 'ObjFoo'.
    SubClass decorator error.

Arguments passed into function must match the same number of SubClass Types.
If not the same count then a ``ValueError`` is rasied.

.. code-block:: python

    >>> do_something(Foo(), ObjFoo(), Bar())
    ValueError: Invalid number of arguments for do_something()
    SubClass decorator error.

Multi Choice
++++++++++++

.. code-block:: python

    from kwhelp.decorator import SubClass

    @SubClass((FooBar, ObjFoo),(Color, Obj))
    def do_something(*args):
        return str(first), str(last)

This call to ``do_something`` raises no errors.

.. code-block:: python

    >>> print(do_something(FooBar(), Color.RED))
    ['FooBar', 'RED']

This call to ``do_something`` raised ``TypeError`` due to first arg
not being a subclass of ``FooBar`` or ``ObjFoo``.

.. code-block:: python

    >>> print(do_something(Foo(), Color.RED))
    TypeError: Arg in 1st position is expected to be of a subclass of 'ObjFoo' or 'FooBar'.
    SubClass decorator error.


Decorating with Key, Value
--------------------------

Decorating when a function has key, value pairs for arguments is
the same pattern as ``*args``. SubClass type one matches position one of function.
SubClass type two matches postiion two of function etc...

.. code-block:: python

    from kwhelp.decorator import SubClass

    @SubClass(Foo, ObjFoo, Color)
    def do_something(first, last, color=Color.GREEN):
        return str(first), str(last) , str(color)


.. code-block:: python

    >>> print(do_something(last=ObjFoo(), first=Foo()))
    ('Foo', 'ObjFoo', 'GREEN')

.. code-block:: python

    >>> print(do_something(last=ObjFoo(), first=1))
    TypeError: Arg 'first' is expected be a subclass of 'Foo'.
    SubClass decorator error.

Primitive Types
---------------

In python numbers and str instances are classes. :py:class:`~.decorator.SubClass`
can also be used to test for numbers and strings.

.. code-block:: python

    @SubClass(int, (int, float), str)
    def do_something(first, last, end):
        return first, last , end


.. code-block:: python

    >>> print(do_something(1, 17, "!!!"))
    (1, 17, '!!!')
    >>> do_something(1, 44.556, "!!!")
    (1, 44.556, '!!!')
    >>> print(do_something(1, 44.556))
    ValueError: Invalid number of arguments for do_something()
    SubClass decorator error.
    >>> print(do_something(1, 44.556, 10))
    TypeError: Arg 'end' is expected be a subclass of 'str'.
    SubClass decorator error.

Option opt_all_args
-------------------

``opt_all_args`` argument allows the last class type passed into :py:class:`~.decorator.SubClass` to
validate all remaining arguments of wrapped function.

For more examples see :doc:`/source/general/dec_feature/opt_all_args`.

.. code-block:: python

    @SubClass(float, (float, int), opt_all_args=True)
    def sum_num(*args):
        return sum(args)

The first arg of ``sum_num`` must be a ``float``. Remaining args can be ``float`` or ``int``.

.. code-block:: python

    >>> print(sum_num(1.3, 44.556, 10, 22, 45, 7.88))
    130.736
    >>> print(sum_num(1, 44.556, 10, 22, 45, 7.88))
    TypeError: Arg in 1st position is expected to be of a subclass of 'float'.
    SubClass decorator error.
    >>> print(sum_num(1.3, 44.556, 10, 22, 45, 7.88, "77"))
    TypeError: Arg in 7th position is expected to be of a subclass of 'float' or 'int'.
    SubClass decorator error.

Opton opt_args_filter
---------------------

The arguments are validated by :py:class:`~.decorator.SubClass` can be filtered by setting ``opt_args_filter`` option. 

For more examples see :doc:`/source/general/dec_feature/opt_args_filter`.

In the following example all ``*args`` must of or derived from clase ``Base``.
``opt_args_filter=DecArgEnum.ARGS`` filters ``SubClass`` to only process ``*args``.

.. code-block:: python

    from kwhelp.decorator import SubClass, DecArgEnum

    @SubClass(Base, opt_all_args=True, opt_args_filter=DecArgEnum.ARGS)
    def foo(*args, msg: str):
        result = [str(t) for t in args]
        return msg + ', '.join(result)

.. code-block:: python

    >>> result = foo(Foo(), Bar(), FooBar(), ObjFoo(), msg='Summary: ')
    >>> print(result)
    Summary: Foo, Bar, FooBar, Foo
    >>> result = foo(Foo(), Bar(), FooBar(), ObjFoo(), msg='Summary: ')
    TypeError: Arg in 4th position is expected to be of a subclass of 'Base'.
    SubClass decorator error.


Combined Decorators
-------------------

:py:class:`~.decorator.SubClass` can be combined with other decorators.

The following example limits how many args are allowed by applying
:py:class:`~.decorator.ArgsMinMax` decorator.

.. code-block:: python

    from kwhelp.decorator import SubClass, ArgsMinMax

    @ArgsMinMax(max=6)
    @SubClass(float, (float, int), opt_all_args=True)
    def sum_num(*args):
        return sum(args)

.. code-block:: python

    >>> print(sum_num(1.3, 44.556, 10, 22, 45, 7.88))
    130.736
    >>> print(sum_num(1, 44.556, 10, 22, 45, 7.88, 100))
    ValueError: Invalid number of args pass into 'sum_num'.
    Expected max of '6'. Got '7' args.
    ArgsMinMax decorator error.