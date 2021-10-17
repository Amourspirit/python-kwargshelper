Assign Rule Checking
====================

Rule checking can be done by adding ``rules_all`` and/or ``rules_any`` to :py:meth:`~.KwargsHelper.assign` method.
Rule checking ensures a value of ``**kwargs`` values matches all rules before assign to
current instance of class.

All rules
---------

In the following example attribute ``speed`` can be a positive ``float`` or a positive ``int``.
All other values will result in an error.



Any rules
---------

In the following example attribute ``speed`` can be a positive ``float`` or a positive ``int``.
All other values will result in an error.

.. code-block:: python

    from kwhelp import KwargsHelper
    import kwhelp.rules as rules

    class MyClass:
        def __init__(self, **kwargs):
            kw = KwargsHelper(self, {**kwargs})
            kw.assign(key="speed", rules_any=[
                rules.RuleIntPositive,
                rules.RuleFloatPositive
            ])

.. code-block:: python

    >>> myclass = MyClass(speed=123)
    >>> print(myclass._speed)
    123

.. code-block:: python

    >>> myclass = MyClass(speed=19.8)
    >>> print(myclass._speed)
    19.8

.. code-block:: python

    >>> myclass = MyClass(speed=-123)
    ValueError: Arg error: 'speed' must be a positive int value

.. code-block:: python

    >>> myclass = MyClass(speed=-19.8)
    TypeError: Argument Error: 'speed' is expecting type of 'int'. Got type of 'float'

.. code-block:: python

    >>> myclass = MyClass(speed="a")
    TypeError: Argument Error: 'speed' is expecting type of 'int'. Got type of 'str'

Included Rules
--------------

.. include:: ../../inc/rules_list.rst