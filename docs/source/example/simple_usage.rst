Simple usage
============

**Example:**

.. code-block:: python
    :caption: Custom Class

    from kwhelp import KwargsHelper
    import kwhelp.rules as rules

    class MyClass:
        def __init__(self, **kwargs):
            self._loop_count = -1
            kw = KwargsHelper(self, {**kwargs}, field_prefix='')
            kw.assign(key='exporter', types=[str], default='None')
            kw.assign(key='name', types=[str], default='unknown')
            kw.assign(key='file_name', rules_all=[rules.RuleStrNotNullOrEmpty])
            kw.assign(key='loop_count', rules_all=[rules.RuleIntPositive],
                    default=self._loop_count)

.. code-block:: python
    :caption: Simple assignment

    >>> my_class = MyClass(file_name='data.html', name='Best Doc', loop_count=1)
    >>> print(my_class.exporter)
    None
    >>> print(my_class.file_name)
    data.html
    >>> print(my_class.name)
    Best Doc
    >>> print(my_class.loop_count)
    1

.. code-block:: python
    :caption: Simple assignment

    >>> my_class = MyClass(exporter='json', file_name='data.json', loop_count=3)
    >>> print(my_class.exporter)
    json
    >>> print(my_class.file_name)
    data.json
    >>> print(my_class.name)
    None
    >>> print(my_class.loop_count)
    3

**Validation Failure**

Raises an error because ``loop_count`` is default  is ``-1`` and
:py:class:`~.rules.RuleIntPositive` is added to rules.

.. code-block:: python
    :caption: Fails validation example

    >>> try:
    >>>     my_class = MyClass(exporter='html', file_name='data.html', name='Best Doc')
    >>> except Exception as e:
    >>>    print(e)
    Arg error: 'loop_count' must be a positive int value

.. seealso::

    :doc:`KwargsHelper <../kwhelp/KwargsHelper>`,
    :doc:`Rules <../kwhelp/rules/index>`