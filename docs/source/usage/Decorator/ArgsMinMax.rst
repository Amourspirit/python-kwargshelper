ArgsMinMax Usage
================

:py:class:`~.decorator.ArgsMinMax` decorartor that sets the min and/or max number of args that can be added to a function.

Includes features:

    * :doc:`/source/general/dec_feature/ftype`
    * :doc:`/source/general/dec_feature/opt_return`

Single Length
-------------

Decorator can be applied with a min Length. In the following example
if less than ``3`` args are passed into ``foo`` a ``ValueError`` will be raised

.. code-block:: python

    from kwhelp.decorator import ArgsMinMax

    @ArgsMinMax(min=3)
    def foo(*args):
        return len(args)

Passing in three arg values works as expected.

.. code-block:: python

    >>> result = foo("a", "b", "c")
    >>> print(result)
    3

Passing in two args when three are expected raises a ``ValueError``

.. code-block:: python

    >>> result = foo("a", "b")
    ValueError: Invalid number of args pass into 'foo'.
    Expected min of 3. Got '2' args.
    ArgsMinMax decorator Error.

Min and Max
----------------

It is possible to set min and max allowed arguments.

.. code-block:: python

    from kwhelp.decorator import ArgsMinMax

    @ArgsMinMax(min=3, max=5)
    def foo(*args):
        return len(args)

Passing in ``3`` args.

.. code-block:: python

    >>> result = foo("a", "b", "c")
    >>> print(result)
    3

Passing in ``5`` args.

.. code-block:: python

    >>> result = foo("a", "b", "c", "d", "e")
    >>> print(result)
    5

Passing in ``6`` args result in a ``ValueError``.

.. code-block:: python

    >>> result = foo("a", "b", "c", "d", "e", "f")
    ValueError: Invalid number of args pass into 'foo'.
    Expected min of 3. Expected max of 5. Got '6' args.
    ArgsMinMax decorator Error.

Class
-----

Decorator can be used on class methods by setting ``ftype`` arg. to a value of
:py:class:`~.decorator.DecFuncEnum`.

Normal class
++++++++++++

.. code-block:: python

    from kwhelp.decorator import ArgsMinMax

    class Foo:
        @ArgsMinMax(max=6, ftype=DecFuncEnum.METHOD)
        def __init__(self, *args): pass

        @ArgsMinMax(3, 5, ftype=DecFuncEnum.METHOD)
        def bar(self, *args): pass

Static method
+++++++++++++

.. code-block:: python

    from kwhelp.decorator import ArgsMinMax

    class Foo:
        @staticmethod
        @ArgsMinMax(min=3 max=5, ftype=DecFuncEnum.METHOD_STATIC)
        def bar(self, *args): pass

Class method
++++++++++++

.. code-block:: python

    from kwhelp.decorator import ArgsMinMax

    class Foo:
        @staticmethod
        @ArgsMinMax(min=3 max=5, ftype=DecFuncEnum.METHOD_CLASS)
        def bar(self, *args): pass