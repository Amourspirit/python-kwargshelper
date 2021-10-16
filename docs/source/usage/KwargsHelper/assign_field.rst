Assign Field Value
==================

Field value can be assigned by adding ``field`` arg to :py:meth:`~.KwargsHelper.assign` method.
By default field values are key values with ``_`` prepended. If ``key="speed"`` then ``field``
defaults to ``_speed`` and thus attribute with the name of ``_speed`` is a assigned to class instance.
Setting ``field`` arg overrides attribute name that is assigned to current class instance.

.. code-block:: python

    from kwhelp import KwargsHelper
    import kwhelp.rules as rules

    class MyClass:
        def __init__(self, **kwargs):
            kw = KwargsHelper(self, {**kwargs})
            kw.assign(key="speed", field="race_speed", require=True,
                rules=[rules.RuleIntPositive])
            kw.assign(key="unit", field="unit", default="MPH",
                rules=[rules.RuleStrNotNullOrEmpty])

.. code-block:: python

    >>> myclass = MyClass(speed=123)
    >>> print(myclass.race_speed)
    123
    >>> print(myclass.unit)
    MPH

.. code-block:: python

    >>> myclass = MyClass(speed=123, unit="KPH")
    >>> print(myclass._speed)
    123
    >>> print(myclass._unit)
    KPH

.. note::
    Default prefix for all field can be set by setting ``field_prefix`` arg of :py:meth:`KwargsHelper <.KwargsHelper.__init__>` constructor.
