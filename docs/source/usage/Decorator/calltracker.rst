Calltracker Usage
=================

:py:mod:`~.decorator.calltracker` decorator method that adds ``has_been_called`` attribute to decorated method.

| ``has_been_called`` is ``False`` if method has not been called.
| ``has_been_called`` is ``True`` if method has been called.

.. code-block:: python

    from kwhelp.decorator import calltracker

    @calltracker
    def foo(msg):
        print(msg)

.. code-block:: python

    >>> print(foo.has_been_called)
    False
    >>> foo("Hello World")
    Hello World
    >>> print(foo.has_been_called)
    True

.. note::

    This decorator needs to be the topmost decorator applied to a method