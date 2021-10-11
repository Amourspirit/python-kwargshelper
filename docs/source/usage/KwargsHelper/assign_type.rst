Assign Type Checking
====================

Type checking can be done by adding ``types`` to :py:meth:`~.KwargsHelper.assign` method.
Type checking ensures the type of ``**kwargs`` values that are assigned to attributes of current instance of class.

.. code-block:: python

    from kwhelp import KwargsHelper

    class MyClass:
        def __init__(self, **kwargs):
            kw = KwargsHelper(self, {**kwargs})
            kw.assign(key="speed", types=[int, float])

.. code-block:: python

    >>> myclass = MyClass(speed=123)
    >>> print(myclass._speed)
    123

.. code-block:: python

    >>> myclass = MyClass(speed=19.8)
    >>> print(myclass._speed)
    19.8

.. code-block:: python

    >>> myclass = MyClass(speed="a")
    TypeError: MyClass arg 'speed' is expected to be of '<class 'int'>' but got 'str'
