ArgsLen Usage
=============

:py:class:`~.decorator.ArgsLen` decorartor that sets the number of args that can be added to a function.

Includes features:

    * :doc:`/source/general/dec_feature/ftype`
    * :doc:`/source/general/dec_feature/opt_return`

Single Length
-------------

Decorator can be applied with a single set Length. In the following example
if anything other than ``3`` args are passed into ``foo`` a ``ValueError`` will be raised

.. code-block:: python

    from kwhelp.decorator import ArgsLen

    @ArgsLen(3)
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
    Expected Length: 3. Got '2' args.
    ArgsLen decorator Error.

Multiple Lengths
----------------

It is possible to allow more then one length to function by passing in multilple ``int`` values to decorator.

.. code-block:: python

    from kwhelp.decorator import ArgsLen

    @ArgsLen(3, 5)
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

Passing in ``4`` args result in a ``ValueError``.

.. code-block:: python

    >>> result = foo("a", "b", "c", "d")
    ValueError: Invalid number of args pass into 'foo'.
    Expected Lengths: 3, 5. Got '4' args.
    ArgsLen decorator Error.

Ranges
------

It is possible to allow more then one length to function by passing in
pairs of ``int`` values in the form of iterable values such as list or tuple values to decorator.

The following example allows 3, 4, 5, 7, 8, 9 args.
Note that 1, 2, 6 or greater than 9 args will result in a ``ValueError``.

.. code-block:: python

    from kwhelp.decorator import ArgsLen

    @ArgsLen((3, 5), (7, 9))
    def foo(*args):
        return len(args)

Passing in ``3`` args.

.. code-block:: python

    >>> result = foo("a", "b", "c")
    >>> print(result)
    3

Passing in ``8`` args.

.. code-block:: python

    from kwhelp.decorator import ArgsLen

    >>> result = foo("a", "b", "c", "d", "e", "f", "g", "h")
    >>> print(result)
    8

Passing in ``6`` args.

.. code-block:: python

    >>> result = foo("a", "b", "c", "d", "e", "f")
    ValueError: Invalid number of args pass into 'foo'.
    Expected Ranges: (3, 5), (7, 9). Got '6' args.
    ArgsLen decorator Error.

Ranges & Lengths
----------------

Ranges and lengths can be combined when needed.

The following example allows 3, 4, 5, 7, 8, 9 args.
Note that 1, 2, 6 or greater than 9 args will result in a ``ValueError``.

.. code-block:: python

    from kwhelp.decorator import ArgsLen

    @ArgsLen(3, 4, 5, (7, 9))
    def foo(*args):
        return len(args)

Passing in ``3`` args.

.. code-block:: python

    >>> result = foo("a", "b", "c")
    >>> print(result)
    3

Passing in ``8`` args.

.. code-block:: python

    >>> result = foo("a", "b", "c", "d", "e", "f", "g", "h")
    >>> print(result)
    8

Passing in ``6`` args.

.. code-block:: python

    >>> result = foo("a", "b", "c", "d", "e", "f")
    ValueError: Invalid number of args pass into 'foo'.
    Expected Lengths: 3, 4, 5. Expected Range: (7, 9). Got '6' args.
    ArgsLen decorator Error.

Class
-----

Decorator can be used on class methods by setting ``ftype`` arg. to a value of
:py:class:`~.decorator.DecFuncEnum`.

Normal class
++++++++++++

.. code-block:: python

    from kwhelp.decorator import ArgsLen

    class Foo:
        @ArgsLen(0, (2, 4), ftype=DecFuncEnum.METHOD)
        def __init__(self, *args): pass

        @ArgsLen(3, 5, ftype=DecFuncEnum.METHOD)
        def bar(self, *args): pass

Static method
+++++++++++++

.. code-block:: python

    from kwhelp.decorator import ArgsLen

    class Foo:
        @staticmethod
        @ArgsLen(3, 5, ftype=DecFuncEnum.METHOD_STATIC)
        def bar(self, *args): pass

Class method
++++++++++++

.. code-block:: python

    from kwhelp.decorator import ArgsLen

    class Foo:
        @staticmethod
        @ArgsLen(3, 5, ftype=DecFuncEnum.METHOD_CLASS)
        def bar(self, *args): pass
