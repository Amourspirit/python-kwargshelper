RuleCheckAllKw Usage
====================

:py:class:`~.decorator.RuleCheckAllKw` decorator allows each arg of a function match all rules specified.
Each arg can have seperate rules applied.

:py:class:`~.decorator.RuleCheckAllKw` constructor args ``arg_info`` and ``rules``  work together.
``arg_info`` is a dictionary with a key of ``str`` that matches an arg name of the function that
is being decorated.
``arg_info`` value is one of the following:

    * ``int`` is an index of an item in ``rules``
    *  ``IRule`` a rule to match
    *  ``Iterator[IRule]`` a list of rules to match

``arg_info`` can be :ref:`mixed <mixed-arg_info>`.

``rules`` is a list of rules to match. Each element is an :py:class:`~.rules.IRule` or a list of :py:class:`~.rules.IRule`.

Custom IRule
------------

Custom :py:class:`~.rules.IRule` class that limits value to a max ``int`` value of ``100``.

.. include:: /source/inc/ex/RuleIntMax100.rst

Example Usage
-------------

:py:class:`~.decorator.RuleCheckAllKw` decorated function.

.. code-block:: python

    from kwhelp.decorator import RuleCheckAllKw
    import kwhelp.rules as rules

    @RuleCheckAllKw(arg_info={"speed": 0, "limit": 1, "hours": 1, "name": 2},
                    rules=[rules.RuleIntPositive,
                            (rules.RuleIntPositive, RuleIntMax100),
                            rules.RuleStrNotNullEmptyWs])
    def speed_msg(speed, limit, **kwargs) -> str:
        name = kwargs.get('name', 'You')
        if limit > speed:
            msg = f"Current speed is '{speed}'. {name} may go faster as the limit is '{limit}'."
        elif speed == limit:
            msg = f"Current speed is '{speed}'. {name} are at the limit."
        else:
            msg = f"Please slow down limit is '{limit}' and current speed is '{speed}'."
        if 'hours' in kwargs:
            msg = msg + f" Current driving hours is '{kwargs['hours']}'."
        return msg

.. code-block:: python

    >>> result = speed_msg(speed=45, limit=60)
    >>> print(result)
    Current speed is '45'. You may go faster as the limit is '60'.

.. code-block:: python

    >>> result = speed_msg(speed=45, limit=60, name="John")
    >>> print(result)
    Current speed is '45'. John may go faster as the limit is '60'.

.. code-block:: python

    >>> result = speed_msg(speed=66, limit=60, hours=3, name="John")
    >>> print(result)
    Please slow down limit is '60' and current speed is '66'. Current driving hours is '3'.


If any rule fails validation then a :py:class:`~.exceptions.RuleError` is raised.

.. code-block:: python

    >>> result = speed_msg(speed=-2, limit=60)
    kwhelp.exceptions.RuleError: RuleError: Argument: 'speed' failed validation. Rule 'RuleIntPositive' Failed validation.
    Expected the following rule to match: RuleIntPositive.
    Inner Error Message: ValueError: Arg error: 'speed' must be a positive int value

.. code-block:: python

    >>> result = speed_msg(speed=66, limit=60, name="  ")
    RuleError: Argument: 'name' failed validation. Rule 'RuleStrNotNullEmptyWs' Failed validation.
    Expected the following rule to match: RuleStrNotNullEmptyWs.
    Inner Error Message: ValueError: Arg error: 'name' must not be empty or whitespace str

.. _mixed-arg_info:

``speed_msg`` decorated with a mixed ``arg_info`` with ``IRule`` instance and index to ``rules``.

.. code-block:: python

    from kwhelp.decorator import RuleCheckAllKw
    import kwhelp.rules as rules

    @RuleCheckAllKw(arg_info={"speed": rules.RuleIntPositive, "limit": 0,
                        "hours": 0, "name": rules.RuleStrNotNullEmptyWs},
                    rules=[(rules.RuleIntPositive, RuleIntMax100)])
    def speed_msg(speed, limit, **kwargs) -> str:
        name = kwargs.get('name', 'You')
        if limit > speed:
            msg = f"Current speed is '{speed}'. {name} may go faster as the limit is '{limit}'."
        elif speed == limit:
            msg = f"Current speed is '{speed}'. {name} are at the limit."
        else:
            msg = f"Please slow down limit is '{limit}' and current speed is '{speed}'."
        if 'hours' in kwargs:
            msg = msg + f" Current driving hours is '{kwargs['hours']}'."
        return msg

Included Rules
--------------

.. include:: ../../inc/rules_list.rst
