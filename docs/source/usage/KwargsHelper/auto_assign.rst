Auto_assign Usage
=================

:py:meth:`.KwargsHelper.auto_assign` method automatically assigns all key-value pairs to class.

Assign with no args
-------------------

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


Assign with type checking
-------------------------

By setting the optional arg ``types`` of :py:meth:`.KwargsHelper.auto_assign`
it is possible to restrict what types can be assigned.

Assigns all of the key, value pairs passed into constructor to class instance if
the value is of type ``int`` or ``float``. Any other type results in an error.

.. code-block:: python

    from kwhelp import KwargsHelper

    class MyClass:
        def __init__(self, **kwargs):
            kw = KwargsHelper(originator=self, obj_kwargs={**kwargs}, field_prefix='')
            kw.auto_assign(types=[int, float])

Any arg assigned with a value of type ``int`` or ``float`` is automatically assigned.

.. code-block:: python

    >>> myclass = MyClass(speed = 123, distance = 557.46)
    >>> print(myclass.speed)
    123
    >>> print(myclass.distance)
    557.46

Assigning an arg with a value that is not of type ``int`` or ``float`` result is an error.

.. code-block:: python

    >>> myclass = MyClass(speed = "Fast", distance = 557.46)
    TypeError: MyClass arg 'speed' is expected to be of '<class 'int'> | <class 'float'>' but got 'str'

Assign with Rule checking
-------------------------

All Rules
+++++++++

By setting the optional arg ``rules_all`` of :py:meth:`.KwargsHelper.auto_assign`
it is possible to set rules that must all be met for key, values to be successfully assigned.

.. code-block:: python

    from kwhelp import KwargsHelper
    import kwhelp.rules as rules

    class MyClass:
        def __init__(self, **kwargs):
            kw = KwargsHelper(originator=self, obj_kwargs={**kwargs}, field_prefix='')
            kw.auto_assign(rules_all=[rules.RuleNotNone, rules.RuleFloatPositive])

Any arg assigned with a value of ``float`` is automatically assigned.

.. code-block:: python

    >>> myclass = MyClass(speed = 99.999, distance = 557.46)
    >>> print(myclass.speed)
    99.999
    >>> print(myclass.distance)
    557.46

Assigning an arg with a value that is not ``float`` result is an error.

.. code-block:: python

    >>> myclass = MyClass(speed = 99.999, distance = 55)
    RuleError: Argument: 'distance' failed validation. Rule 'RuleFloatPositive' Failed validation.
    Expected all of the following rules to match: RuleNotNone, RuleFloatPositive.
    Inner Error Message: TypeError: Argument Error: 'distance' is expecting type of 'float'. Got type of 'int'

Assigning an arg with a value that is a negative ``float`` result is an error.

.. code-block:: python

    >>> myclass = MyClass(speed = 99.999, distance = -128.09)
    RuleError: Argument: 'distance' failed validation. Rule 'RuleFloatPositive' Failed validation.
    Expected all of the following rules to match: RuleNotNone, RuleFloatPositive.
    Inner Error Message: ValueError: Arg error: 'distance' must be a positive float value

Any Rules
+++++++++

By setting the optional arg ``rules_any`` of :py:meth:`.KwargsHelper.auto_assign`
it is possible to set rules that must have at least one match for key, values to be successfully assigned.

.. code-block:: python

    from kwhelp import KwargsHelper
    import kwhelp.rules as rules

    class MyClass:
        def __init__(self, **kwargs):
            kw = KwargsHelper(originator=self, obj_kwargs={**kwargs}, field_prefix='')
            kw.auto_assign(rules_any=[rules.RuleIntPositive, rules.RuleFloatPositive])

Any arg assigned with a value of ``int`` or ``float`` is automatically assigned.

.. code-block:: python

    >>> myclass = MyClass(speed = 99.999, distance = 558)
    >>> print(myclass.speed)
    99.999
    >>> print(myclass.distance)
    558

Assigning an arg with a value that is not ``int`` or ``float`` result is an error.

.. code-block:: python

    >>> myclass = MyClass(speed = 'Fast', distance = 55)
    RuleError: Argument: 'speed' failed validation. Rule 'RuleIntPositive' Failed validation.
    Expected at least one of the following rules to match: RuleIntPositive, RuleFloatPositive.
    Inner Error Message: TypeError: Argument Error: 'speed' is expecting type of 'int'. Got type of 'str'

Assigning an arg with a value that is a negative ``int`` result is an error.

.. code-block:: python

    >>> myclass = MyClass(speed = 99.999, distance = -35)
    RuleError: Argument: 'distance' failed validation. Rule 'RuleIntPositive' Failed validation.
    Expected at least one of the following rules to match: RuleIntPositive, RuleFloatPositive.
    Inner Error Message: ValueError: Arg error: 'distance' must be a positive int value

.. seealso::

    * :py:meth:`.KwargsHelper.auto_assign`
    * :py:meth:`.KwargsHelper.add_handler_before_assign_auto`
    * :py:class:`.KwargsHelper`
    * :py:class:`.BeforeAssignAutoEventArgs`
    * :doc:`auto_assign_callback`
    * :doc:`assign_rules`
