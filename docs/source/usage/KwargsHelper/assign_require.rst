Assign Require Arg
==================

Required args can be done by adding ``require`` args to :py:meth:`~.KwargsHelper.assign` method.
If a required args is missing then a ``ValueError`` will be raised.

.. code-block:: python

    from kwhelp import KwargsHelper

    class MyClass:
        def __init__(self, **kwargs):
            kw = KwargsHelper(self, {**kwargs})
            kw.assign(key="speed", require=True)
            kw.assign(key="unit")

.. code-block:: python

    >>> myclass = MyClass(speed=123, unit="KPH")
    >>> print(myclass._speed)
    123
    >>> print(myclass._unit)
    KPH

.. code-block:: python

    >>> myclass = MyClass(unit="KPH")
    ValueError: MyClass arg 'speed' is required
