SubClass Usage
===============

:py:class:`~.decorator.SubClass` decorator reqires that each args of a function match a ``type``.

Includes features:

    * :doc:`/source/general/dec_feature/ftype`
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

Expected args pass valadation.

.. code-block:: python

    >>> print(do_something(Foo(), ObjFoo()))
        ['Foo', 'ObjFoo']

Types dictate that if first arg is not a subclass of ``Foo`` or
first arg is not a subclass of ``ObjFoo`` then an error will be raised.

.. code-block:: python

    >>> result = do_something(Foo(), Obj())
    TypeError: Arg in 2nd position is expected to be of a subclass of '<class '__main__.ObjFoo'>'.

Arguments passed into function must match the same number of SubClass Types.
If not the same count then a ``ValueError`` is rasied.

.. code-block:: python

    >>> do_something(Foo(), ObjFoo, Bar())
    ValueError: Invalid number of arguments for do_something()

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
    TypeError: Arg in 1st position is expected to be of a subclass of '<class '__main__.FooBar'> | <class '__main__.ObjFoo'>'.


Decorating with Key, Value
--------------------------

Decorating when a function has key, value pairs for arguments is
the same pattern as ``*args``. SubClass type one matches position one of function.
SubClass type two matches postiion two of function etc...

.. code-block:: python

    from kwhelp.decorator import SubClass

    @SubClass(Foo, ObjFoo, [Color])
    def do_something(first, last, color=Color.GREEN):
        return str(first), str(last) , str(color)


.. code-block:: python

    >>> print(do_something(last=ObjFoo(), first=Foo()))
    ('Foo', 'ObjFoo', 'GREEN')

.. code-block:: python

    >>> result = speed_msg(speed=66, limit=60, hours=4.7)
    >>> print(result)
    Please slow down limit is '60' and you are currenlty going '66'. Current driving hours is '4.7

Types dictate that if a type is not ``int`` or ``float`` then an error will be raised.

.. code-block:: python

    >>> result = speed_msg(speed=45, limit="Fast")
    TypeError: Arg 'limit' is expected to be of '<class 'int'> | <class 'float'>' but got 'str'