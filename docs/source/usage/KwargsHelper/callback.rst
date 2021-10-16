Callback Usage
==============

Callbacks can be used to hook some of :py:class:`~.KwargsHelper` events.

This class as two callback methods. ``MyClass._arg_before_cb()`` method is called before attribute assignment.
``MyClass._arg_after_cb()`` method is called after attribute assignment.

.. include:: /source/inc/ex/KwargsHelper_cb.rst

In the following case ``my_class.name`` value is changed from ``"unknown"`` to ``"None"`` in callback
``MyClass._arg_before_cb()`` method.

.. include:: /source/inc/ex/KwargsHelper_cb_01.rst

In the following case ``loop_count`` is a negative number which triggers a :py:class:`~.CancelEventError`
in ``MyClass._arg_before_cb()``.

.. include:: /source/inc/ex/KwargsHelper_cb_02.rst

.. note::

    If :py:meth:`KwargsHelper constructor <.KwargsHelper.__init__>` has ``cancel_error`` set to ``False`` then
    no error will be raised when :py:attr:`.BeforeAssignEventArgs.cancel` is set to ``True``.

.. seealso::

    * :py:class:`~.KwargsHelper`
    * :py:meth:`.KwargsHelper.add_handler_after_assign`
    * :py:meth:`.KwargsHelper.add_handler_after_assign_auto`
    * :py:meth:`.KwargsHelper.add_handler_before_assign`
    * :py:meth:`.KwargsHelper.add_handler_before_assign_auto`
    * :py:class:`~.AfterAssignEventArgs`
    * :py:class:`~.BeforeAssignEventArgs`
    * :py:class:`~.AssignBuilder`
    * :doc:`auto_assign_callback`
