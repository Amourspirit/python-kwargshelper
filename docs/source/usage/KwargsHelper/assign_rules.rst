Assign Rule Checking
====================

Rule checking can be done by adding ``rules_all`` and/or ``rules_any`` to :py:meth:`~.KwargsHelper.assign` method.
Rule checking ensures a value of ``**kwargs`` values matches all rules before assign to
current instance of class.

All rules
---------

In the following example attribute ``speed`` can be a positive ``float`` or ``int`` zero.
All other values will result in an error. Arg ``rules_all`` of :py:meth:`~.KwargsHelper.assign`
method validates as ``True`` only if all :py:class:`~.IRule` match.
Trying to assign any other type or value results in an error.

Custom Rule for a maximum ``int`` value of 100

.. include:: /source/inc/ex/RuleIntMax100.rst

.. code-block:: python

    from kwhelp import KwargsHelper
    import kwhelp.rules as rules

    class MyClass:
        def __init__(self, **kwargs):
            kw = KwargsHelper(originator=self, obj_kwargs={**kwargs}, field_prefix="")
            kw.assign(key="speed", rules_all=[
                rules.RuleIntPositive,
                RuleIntMax100
            ])

Assign ``int``.

.. code-block:: python

    >>> myclass = MyClass(speed = 12)
    >>> print(myclass.speed)
    12

Assign ``int`` greater then 100.

.. code-block:: python

    >>> myclass = MyClass(speed = 126)
    ValueError: Arg error: 'speed' must be equal or less than 100

Assign ``int`` negative.

.. code-block:: python

    >>> myclass = MyClass(speed = -3)
    ValueError: Arg error: 'speed' must be a positive int value

Assign ``float``.

.. code-block:: python

    >>> myclass = MyClass(speed = 22.4)
    TypeError: Argument Error: 'speed' is expecting type of 'int'. Got type of 'float'

Any rules
---------

In the following example attribute ``speed`` can be a positive ``float`` or ``int`` zero.
All other values will result in an error. Arg ``rules_all`` of :py:meth:`~.KwargsHelper.assign`
method validates as ``True`` only if all :py:class:`~.IRule` match.
Trying to assign any other type or value results in an error.

.. code-block:: python

    from kwhelp import KwargsHelper
    import kwhelp.rules as rules

    class MyClass:
        def __init__(self, **kwargs):
            kw = KwargsHelper(originator=self, obj_kwargs={**kwargs}, field_prefix="")
            kw.assign(key="speed", rules_any=[
                rules.RuleFloatPositive,
                rules.RuleIntZero
            ])

Assign ``int``.

.. code-block:: python

    >>> myclass = MyClass(speed = 123.55)
    >>> print(myclass.speed)
    123.55

Assign ``int`` zero.

.. code-block:: python

    >>> myclass = MyClass(speed = 0)
    >>> print(myclass.speed)
    0

Assign ``float`` zero.

.. code-block:: python

    >>> myclass = MyClass(speed = 0.0)
    >>> print(myclass.speed)
    0.0

Assign ``int`` negative.

.. code-block:: python

    >>> myclass = MyClass(speed = -123)
    TypeError: Argument Error: 'speed' is expecting type of 'float'. Got type of 'int'

Assign ``str``.

.. code-block:: python

    >>> myclass = MyClass(speed="a")
    TypeError: Argument Error: 'speed' is expecting type of 'float'. Got type of 'str'

Included Rules
--------------

.. include:: ../../inc/rules_list.rst