Assign Default Value
====================

Default value can be assigned by adding ``default`` args to :py:meth:`~.KwargsHelper.assign` method.

.. code-block:: python

    from kwhelp import KwargsHelper
    import kwhelp.rules as rules

    class MyClass:
        def __init__(self, **kwargs):
            self._duration = "Long"
            kw = KwargsHelper(self, {**kwargs})
            kw.assign(key="speed", require=True, rules=[rules.RuleIntPositive])
            kw.assign(key="unit", default="MPH", rules=[rules.RuleStrNotNullOrEmpty])
            kw.assign(key="duration", default=self._duration,
                rules=[rules.RuleStrNotNullOrEmpty])

.. code-block:: python

    >>> myclass = MyClass(speed=123, unit="KPH")
    >>> print(myclass._speed)
    123
    >>> print(myclass._unit)
    KPH
    >>> print(myclass._duration)
    Long

.. code-block:: python

    >>> myclass = MyClass(speed=123, duration="Short")
    >>> print(myclass._speed)
    123
    >>> print(myclass._unit)
    MPH
    >>> print(myclass._duration)
    Short