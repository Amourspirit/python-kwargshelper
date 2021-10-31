Callcounter Usage
=================

:py:mod:`~.decorator.callcounter` Decorator method that adds ``call_count`` attribute to decorated method.

| ``call_count`` is ``0`` if method has not been called.
| ``call_count`` increases by 1 each time method is been called.

.. code-block:: python

    from kwhelp.decorator import calltracker

    @callcounter
    def foo(msg):
        print(msg)

.. code-block:: python

    >>> print("Call Count:", foo.call_count)
    0
    >>> foo("Hello")
    Hello
    >>> print("Call Count:", foo.call_count)
    1
    >>> foo("World")
    World
    >>> print("Call Count:", foo.call_count)
    2

.. note::

    This decorator needs to be the topmost decorator applied to a method