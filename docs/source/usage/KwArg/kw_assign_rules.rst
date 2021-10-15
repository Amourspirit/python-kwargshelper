Kw_assign Rule Checking
=======================

Rule checking can be done by adding ``rules`` to :py:meth:`~.KwArg.kw_assign` method.
Rule checking ensures a value of ``**kwargs`` values matches all rules before assign to
current instance of class.

In the following example args ``first`` and ``second`` can be a positive ``float`` or a positive ``int``.
All other values will result in an error.

.. code-block:: python

    from kwhelp import KwArg
    import kwhelp.rules as rules

    def my_method(**kwargs) -> str:
        kw = KwArg(**kwargs)
        kw.kw_assign(key='first', require=True, rules=[
            rules.RuleIntPositive,
            rules.RuleFloatPositive
        ])
        kw.kw_assign(key='second', require=True, rules=[
            rules.RuleIntPositive,
            rules.RuleFloatPositive
        ])
        kw.kw_assign(key='msg', types=[str], default='Result:')
        kw.kw_assign(key='end', types=[str])
        first:int = kw.first
        second:int = kw.second
        msg: str = kw.msg
        _result = first + second
        if kw.is_attribute_exist('end'):
            return_msg = f'{msg} {_result}{kw.end}'
        else:
            return_msg = f'{msg} {_result}'
        return return_msg

Included Rules
--------------

.. include:: ../../inc/rules_list.rst