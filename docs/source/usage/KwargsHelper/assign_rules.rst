Assign Rule Checking
====================

Rule checking can be done by adding ``rules`` to :py:meth:`~.KwargsHelper.assign` method.
Rule checking ensures a value of ``**kwargs`` values matches all rules before assign to
current instance of class.

.. code-block:: python

    from kwhelp import KwargsHelper
    import kwhelp.rules as rules

    class MyClass:
        def __init__(self, **kwargs):
            kw = KwargsHelper(self, {**kwargs})
            kw.assign(key="speed", types=[int, float], rules=[
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
    ValueError: Arg error: 'speed' must be a positive float value

.. code-block:: python

    >>> myclass = MyClass(speed="a")
    TypeError: MyClass arg 'speed' is expected to be of '<class 'int'>' but got 'str'
