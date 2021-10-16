Basic Usage
===========

Processing |args| in a class.

:py:class:`.KwargsHelper` class assigns attributes to existing class instance if they are missing.
Each key in |args| is transformed into an attribute name and that attribute name is assigned to current
instance of class if it does not already exist. Be default attribute names is the key name with ``_`` appended. See :ref:`fig-2`

|args| values are assigned to attribue that match keys.

Use :py:class:`.KwargsHelper` class to process |args| in a class.

.. code-block:: python
    :caption: Figure 1
    :name: fig-1

    from kwhelp import KwargsHelper

    class MyClass:
        def __init__(self, **kwargs):
            kw = KwargsHelper(self, {**kwargs})
            kw.auto_assign()

    >>> myclass = MyClass(speed=123)
    >>> print(myclass._speed)
    123

In the following example **attribute** names are transformed to match the **key** name.
This is done by setting ``field_prefix`` to empty string in constructor.
See Also: :py:attr:`.KwargsHelper.field_prefix`

.. code-block:: python
    :caption: Figure 2
    :name: fig-2

    from kwhelp import KwargsHelper

    class MyClass:
        def __init__(self, **kwargs):
            kw = KwargsHelper(originator=self, obj_kwargs={**kwargs}, field_prefix='')
            kw.auto_assign()

.. code-block:: python

    >>> myclass = MyClass(speed=123)
    >>> print(myclass.speed)
    123

.. seealso::

    * :doc:`Example Simple Usage <../../example/simple_usage>`
    * :doc:`../../kwhelp/KwargsHelper`

.. |args| replace:: ``**kwargs``