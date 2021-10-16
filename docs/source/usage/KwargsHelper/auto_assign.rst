Auto_assign Usage
=================

:py:meth:`.KwargsHelper.auto_assign` method automatically assigns all key-value pairs to class.

Assigns all of the key, value pairs  passed into constructor to class instance,
unless the event is canceled in :py:class:`.BeforeAssignAutoEventArgs` via
:py:meth:`.KwargsHelper.add_handler_before_assign_auto` callback.

.. code-block:: python

    from kwhelp import KwargsHelper

    class MyClass:
        def __init__(self, **kwargs):
            kw = KwargsHelper(originator=self, obj_kwargs={**kwargs}, field_prefix='')
            kw.auto_assign()

.. code-block:: python

    >>> myclass = MyClass(speed=123, msg="Hello World")
    >>> print(myclass.speed)
    123
    >>> print(myclass.msg)
    Hello World

.. seealso::

    * :py:meth:`.KwargsHelper.auto_assign`
    * :py:meth:`.KwargsHelper.add_handler_before_assign_auto`
    * :py:class:`.KwargsHelper`
    * :py:class:`.BeforeAssignAutoEventArgs`
    * :doc:`auto_assign_callback`
