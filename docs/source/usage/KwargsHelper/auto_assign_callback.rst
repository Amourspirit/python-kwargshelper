Auto_assign Callback
====================

:py:meth:`.KwargsHelper.auto_assign` method automatically assigns all key-value pairs to class.

Assigns all of the key, value pairs  passed into constructor to class instance,
unless the event is canceled in :py:class:`.BeforeAssignAutoEventArgs` via
:py:meth:`.KwargsHelper.add_handler_before_assign_auto` callback.

``MyClass._arg_before_cb()`` callback method reads conditions before attribue and value are assigned.
If required conditions are not met then cancel can be set.

.. code-block:: python

    from kwhelp import KwargsHelper, AfterAssignAutoEventArgs, BeforeAssignAutoEventArgs

    class MyClass:
        def __init__(self, **kwargs):
            kw = KwargsHelper(originator=self, obj_kwargs={**kwargs}, field_prefix="")
            kw.add_handler_before_assign_auto(self._arg_before_cb)
            kw.add_handler_after_assign_auto(self._arg_after_cb)
            kw.auto_assign()

        def _arg_before_cb(self, helper: KwargsHelper,
                        args: BeforeAssignAutoEventArgs) -> None:
            # callback function before value assigned to attribute
            if args.key == 'loop_count' and args.field_value < 0:
                # cancel will raise CancelEventError unless
                # KwargsHelper constructor has cancel_error=False
                args.cancel = True
            if args.key == 'name' and args.field_value == 'unknown':
                args.field_value = 'None'

        def _arg_after_cb(self, helper: KwargsHelper,
                        args: AfterAssignAutoEventArgs) -> None:
            # callback function after value assigned to attribute
            if args.key == 'name' and args.field_value == 'unknown':
                raise ValueError(
                    f"{args.key} This should never happen. value was suppose to be reassigned")

In the following case key, value args are automatically assigned to class.

.. code-block:: python

    >>> my_class = MyClass(exporter='json', file_name='data.json', loop_count=3)
    >>> print(my_class.exporter)
    json
    >>> print(my_class.file_name)
    data.json
    >>> print(my_class.loop_count)
    3

In the following case ``my_class.name`` value is changed from ``"unknown"`` to ``"None"`` in callback
``MyClass._arg_before_cb()`` method.

.. code-block:: python

    >>> my_class = MyClass(exporter='json', file_name='data.json', loop_count=3, name="unknown")
    >>> print(my_class.exporter)
    json
    >>> print(my_class.file_name)
    data.json
    >>> print(my_class.loop_count)
    3
    >>> print(my_class.name)
    None

In the following case ``loop_count`` is a negative number which triggers a :py:class:`~.CancelEventError`
in ``MyClass._arg_before_cb()``.


.. code-block:: python

    >>> my_class = MyClass(exporter='json', file_name='data.json', loop_count=-1)
    kwhelp.CancelEventError: KwargsHelper.auto_assign() canceled in 'BeforeAssignBlindEventArgs'

.. note::

    If :py:meth:`KwargsHelper constructor <.KwargsHelper.__init__>` has ``cancel_error`` set to ``False`` then
    no error will be raised when :py:attr:`.BeforeAssignAutoEventArgs.cancel` is set to ``True``.

.. seealso::

    * :py:class:`~.KwargsHelper`
    * :py:meth:`.KwargsHelper.add_handler_after_assign`
    * :py:meth:`.KwargsHelper.add_handler_after_assign_auto`
    * :py:meth:`.KwargsHelper.add_handler_before_assign`
    * :py:meth:`.KwargsHelper.add_handler_before_assign_auto`
    * :py:class:`~.AfterAssignAutoEventArgs`
    * :py:class:`~.BeforeAssignAutoEventArgs`
    * :py:class:`~.AssignBuilder`
    * :doc:`auto_assign`
    * :doc:`callback`
