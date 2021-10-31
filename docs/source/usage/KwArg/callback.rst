Callback Usage
==============

Callbacks can be used to hook some of :py:class:`.KwArg` events.

By using the :py:attr:`.KwArg.kwargs_helper` property which is an instance of :py:class:`~.KwargsHelper` it
is possible to use callbacks.

This function has two nested callback functions. ``arg_before_cb()`` function is called before
key, value is assigned to :py:class:`.KwArg` instance. ``arg_after_cb()`` function is called after key, value
is assigned to :py:class:`.KwArg` instance.

.. code-block:: python

    from kwhelp import AfterAssignEventArgs, BeforeAssignEventArgs, KwargsHelper, KwArg

    def my_method(**kwargs) -> str:
        def arg_before_cb(helper: KwargsHelper,
                        args: BeforeAssignEventArgs) -> None:
            # callback function before value assigned to KwArg instance
            if args.key == 'msg':
                if args.field_value == "cancel":
                    # cancel will raise CancelEventError unless
                    # kw.kwargs_helper.cancel_error = False
                    args.cancel = True
                elif args.field_value == "":
                    args.field_value = "Value:"
            if args.key == 'name' and args.field_value == 'unknown':
                args.field_value = 'None'
        def arg_after_cb(helper: KwargsHelper,
                        args: AfterAssignEventArgs) -> None:
            # callback function after value assigned to KwArg instance
            if args.key == 'msg' and args.field_value == "":
                raise ValueError(
                    f"{args.key} This should never happen. value was suppose to be reassigned")
        # main function
        kw = KwArg(**kwargs)
        # assign Callbacks
        kw.kwargs_helper.add_handler_before_assign(arg_before_cb)
        kw.kwargs_helper.add_handler_after_assign(arg_after_cb)
        # assign args
        kw.kw_assign(key='first', require=True, types=[int])
        kw.kw_assign(key='second', require=True, types=[int])
        kw.kw_assign(key='msg', types=[str], default='Result:')
        kw.kw_assign(key='end', types=[str])
        _result = kw.first + kw.second
        if kw.is_attribute_exist('end'):
            return_msg = f'{kw.msg} {_result}{kw.end}'
        else:
            return_msg = f'{kw.msg} {_result}'
        return return_msg


Call back does not make changes to the following result.

.. code-block:: python

    >>> result = my_method(first = 10, second = 22)
    >>> print(result)
    Result: 32

Call back changes ``msg`` from empty string to ``Value:``

.. code-block:: python

    >>> result = my_method(first = 10, second = 22, msg = "")
    >>> print(result)
    Value: 32

Call back raises :py:class:`~.kwhelp.CancelEventError` when ``msg`` equals ``cancel``.

.. code-block:: python

    >>> result = my_method(first = 10, second = 22, msg = "cancel")
    kwhelp.CancelEventError: KwargsHelper.assign() canceled in 'BeforeAssignEventArgs'

.. note::

    If :py:attr:`.KwargsHelper.cancel_error` property is set to ``False`` then
    no error will be raised when :py:attr:`.BeforeAssignEventArgs.cancel` is set to ``True``.

    If no error is raised then :py:attr:`.AfterAssignEventArgs.canceled` can be used to check if
    an event was canceled in :py:class:`.BeforeAssignEventArgs`

.. seealso::

    * :py:class:`~.KwArg`
    * :py:attr:`.KwArg.kwargs_helper`
    * :py:class:`~.KwargsHelper`
    * :py:meth:`.KwargsHelper.add_handler_after_assign`
    * :py:meth:`.KwargsHelper.add_handler_after_assign_auto`
    * :py:meth:`.KwargsHelper.add_handler_before_assign`
    * :py:meth:`.KwargsHelper.add_handler_before_assign_auto`
    * :py:class:`~.AfterAssignEventArgs`
    * :py:class:`~.BeforeAssignEventArgs`
    * :doc:`KwargsHelper Callback Usage <../KwargsHelper/callback>`