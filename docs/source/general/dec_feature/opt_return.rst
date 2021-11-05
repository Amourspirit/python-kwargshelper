opt_return
==========

Many decorators supports *optoinal* ``opt_return`` option.
``opt_return`` sets what will be be returned if validation fails.
Noramlly decorators will raise an error if validation fails.

In the following example by setting ``opt_return`` to ``False``
then when validation fails ``False`` will be returned instead of an error
being raised.

.. code-block:: python

    from kwhelp.decorator import ArgsLen, RuleCheckAll
    from kwhelp import rules

    @ArgsLen(2, opt_return=False)
    @RuleCheckAll(rules.RuleStrNotNullEmptyWs, opt_return=False)
    def is_ab(*args):
        if args[0].lower() == "a" and args[1].lower() == "b":
            return True
        return False

.. code-block:: python

    >>> print(is_ab())
    False
    >>> print(is_ab(1))
    False
    >>> print(is_ab(1, 2))
    False
    >>> print(is_ab('ab'))
    False
    >>> print(is_ab('a', 'b', 'c'))
    False
    >>> print(is_ab('a', 'b'))
    True
    >>> print(is_ab('A', 'B'))
    True
    >>> print(is_ab(["a", "b"]))
    False
    >>> print(is_ab(*["a", "b"]))
    True