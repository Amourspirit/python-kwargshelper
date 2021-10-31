Singleton Usage
===============

:py:mod:`~.decorator.singleton` decorator that makes a class a singleton class

Example class that becomes a singleton class onece attribute is applied.

.. code-block:: python

    from kwhelp.decorator import singleton, RuleCheckAll
    from kwhelp import rules

    @singleton
    class Logger:
        @RuleCheckAll(rules.RuleStrNotNullEmptyWs, ftype=DecFuncEnum.METHOD)
        def log(self, msg):
            print(msg)

All created instances are the same instance.

.. code-block:: python

    >>> logger1 = Logger()
    >>> logger2 = Logger()
    >>> print(logger1 is logger1)
    True

.. seealso::

    :doc:`RuleCheckAll`