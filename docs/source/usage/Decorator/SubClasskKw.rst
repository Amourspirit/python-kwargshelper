SubClasskKw Usage
=================

:py:class:`~.decorator.SubClasskKw` decorator that requires args of a function to match
or be a subclass of types specificed in constructor. Each arg can have seperate rules applied.

Includes features:

    * :doc:`/source/general/dec_feature/ftype`
    * :doc:`/source/general/dec_feature/opt_return`
    * :doc:`/source/general/dec_feature/type_instance_check`

:py:class:`~.decorator.SubClasskKw` constructor args ``arg_info`` and ``rules``  work together.
``arg_info`` is a dictionary with a key of ``str`` that matches an arg name of the function that
is being decorated.
``arg_info`` value is one of the following:

    * ``int`` is an index of an item in ``rules``
    *  ``type`` a type to match

``arg_info`` can be :ref:`mixed <mixed-arg_info>`.

``types`` is a list of type to match.

Example Usage
-------------

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

:py:class:`~.decorator.SubClasskKw` decorated function.

.. code-block:: python

    from kwhelp.decorator import SubClasskKw

    @SubClasskKw(arg_info={"first": 0, "second": 0, "obj": 0, "color": 1},
                types=[(Foo, Obj), Color])
    def myfunc(first, second, **kwargs):
        color = kwargs.get("color", Color.BLUE)
        return (str(first), str(second), str(kwargs['obj']), str(color))

.. code-block:: python

    >>> result = myfunc(first=Foo(), second=ObjFoo(), obj=FooBar())
    >>> print(result)
    ('Foo', 'ObjFoo', 'FooBar', 'BLUE')

.. code-block:: python

    >>> result = myfunc(first=Foo(), second=ObjFoo(), color=Color.RED, obj=FooBar())
    >>> print(result)
    ('Foo', 'ObjFoo', 'FooBar', 'RED')

If types fail validation then a ``TypeError`` is raised.

.. code-block:: python

    >>> result = myfunc(first=Foo(), second=ObjFoo(), color=1, obj=FooBar())
    TypeError: Arg 'color' is expected to be of a subclass of 'Color'.
    SubClasskKw decorator error.

.. _mixed-arg_info:

:py:class:`~.decorator.SubClasskKw` ``arg_info`` contains types and indexes.
Types of ``arg_info`` are requied to match function arguments directly.
Indexes are an index of ``types`` that match function arguments.

.. code-block:: python

    from kwhelp.decorator import SubClasskKw

    @SubClasskKw(arg_info={"first": 0, "second": 0, "obj": 0, "color": Color},
                types=[(Foo, Obj), Color])
    def myfunc(first, second, **kwargs):
        color = kwargs.get("color", Color.BLUE)
        return (str(first), str(second), str(kwargs['obj']), str(color))

.. code-block:: python

    >>> result = myfunc(first=Foo(), second=ObjFoo(), obj=FooBar())
    >>> print(result)
    ('Foo', 'ObjFoo', 'FooBar', 'BLUE')

.. code-block:: python

    >>> result = myfunc(first=Foo(), second=ObjFoo(), color=1, obj=FooBar())
    TypeError: Arg 'color' is expected to be of a subclass of 'Color'.
    SubClasskKw decorator error.

Primitive Types
---------------

In python numbers and str instances are classes. :py:class:`~.decorator.SubClasskKw`
can also be used to test for numbers and strings.

.. code-block:: python

    from kwhelp.decorator import SubClasskKw

    @SubClasskKw(arg_info={"first": 0, "second": 0, "obj": 0, "last": 1},
                types=[(int, float), str])
    def myfunc(first, second, **kwargs):
        last = kwargs.get("last", "The End!")
        return (first, second, kwargs['obj'], last)

.. code-block:: python

    >>> result = myfunc(first=22.55, second=555, obj=-12.45, last="!!!")
    >>> print(result)
    (22.55, 555, -12.45, '!!!')

.. code-block:: python

    >>> result = myfunc(first=22.55, second=555, obj=None, last="!!!")
    >>> print(result)
    TypeError: Arg 'obj' is expected to be of a subclass of 'float' or 'int'.
    SubClasskKw decorator error.