ftype
=====

``ftype`` option  is :py:class:`~.decorator.DecFuncEnum` argument.
``ftype`` sets the type of ``function``, ``method``, ``property`` etc.

Function
--------

Default for ``ftype`` is function. Therefore it is not necessary to set ftype on functions.

.. code-block:: python

    @RuleCheckAll(rules.RuleIntPositive)
    def fib(n: int):
        def _fib(_n, memo={}):
            if _n in memo: return memo[_n]
            if _n <= 2: return 1
            memo[_n] = _fib(_n - 1, memo) + _fib(_n - 2, memo)
            return memo[_n]
        return _fib(n)

Run function.

.. code-block:: python

    >>> print(fib(7))
    8
    >>> print(fib(8))
    13
    >>> print(fib(6))
    21
    >>> print(fib(50))
    2586269025
    >>> print(fib(-50))
    kwhelp.exceptions.RuleError: RuleError: 'fib' error.
    Rule 'RuleIntPositive' Failed validation.
    Expected the following rule to match: RuleIntPositive.
    Inner Error Message: ValueError: Arg error: 'arg' must be a positive int value
    >>> print(fib("3"))
    kwhelp.exceptions.RuleError: RuleError: 'fib' error.
    Rule 'RuleIntPositive' Failed validation.
    Expected the following rule to match: RuleIntPositive.
    Inner Error Message: TypeError: Argument Error: 'arg' is expecting type of 'int'. Got type of 'str'

Class
-----

For class method ``ftype``  is set to ``DecFuncEnum.METHOD``

.. code-block:: python

    class Calc:
        @RuleCheckAll(rules.RuleIntPositive, ftype=DecFuncEnum.METHOD)
        def fib(self, n: int):
            def _fib(_n, memo={}):
                if _n in memo: return memo[_n]
                if _n <= 2: return 1
                memo[_n] = _fib(_n - 1, memo) + _fib(_n - 2, memo)
                return memo[_n]
            return _fib(n)

.. code-block:: python

    >>> c = Calc()
    >>> print(c.fib(7))
    8
    >>> print(c.fib(8))
    13
    >>> print(c.fib(6))
    21
    >>> print(c.fib(50))
    2586269025
    >>> print(c.fib(-50))
    kwhelp.exceptions.RuleError: RuleError: 'fib' error.
    Rule 'RuleIntPositive' Failed validation.
    Expected the following rule to match: RuleIntPositive.
    Inner Error Message: ValueError: Arg error: 'arg' must be a positive int value

Class Property
--------------

For class property ``ftype``  is set to ``DecFuncEnum.PROPERTY_CLASS``

.. code-block:: python

    class Foo:

        @RuleCheckAny(RuleIntPositive, RuleFloatPositive, ftype=DecFuncEnum.METHOD)
        def __init__(self, test_value) -> None:
            self._test = test_value
        
        @property
        def test(self):
            return self._test
        
        @test.setter
        @RuleCheckAny(RuleIntPositive, RuleFloatPositive, ftype=DecFuncEnum.PROPERTY_CLASS)
        def test(self, value):
            self._test = value

.. code-block:: python

    >>> f = Foo(test_value=22)
    >>> print(f.test)
    22
    >>> f.test = 127.899
    >>> print(f.test)
    127.899
    >>> f.test = -33
    kwhelp.exceptions.RuleError: RuleError: 'test' error.
    Rule 'RuleIntPositive' Failed validation.
    Expected at least one of the following rules to match: RuleIntPositive, RuleFloatPositive.
    Inner Error Message: ValueError: Arg error: 'arg' must be a positive int value

Class staticmethod
------------------

For staticmethod method ``ftype``  is set to ``DecFuncEnum.METHOD_STATIC``

.. code-block:: python

    class Calc:
        @staticmethod
        @RuleCheckAll(rules.RuleIntPositive, ftype=DecFuncEnum.METHOD_STATIC)
        def fib(n: int):
            def _fib(_n, memo={}):
                if _n in memo: return memo[_n]
                if _n <= 2: return 1
                memo[_n] = _fib(_n - 1, memo) + _fib(_n - 2, memo)
                return memo[_n]
            return _fib(n)

.. code-block:: python

    >>> print(Calc.fib(7))
    8
    >>> print(Calc.fib(8))
    13
    >>> print(Calc.fib(6))
    21
    >>> print(Calc.fib(50))
    2586269025

Class classmethod
-----------------

For classmethod ``ftype``  is set to ``DecFuncEnum.METHOD_CLASS``

.. code-block:: python

    class Calc:
        @classmethod
        @RuleCheckAll(rules.RuleIntPositive, ftype=DecFuncEnum.METHOD_CLASS)
        def fib(cls, n: int):
            def _fib(_n, memo={}):
                if _n in memo: return memo[_n]
                if _n <= 2: return 1
                memo[_n] = _fib(_n - 1, memo) + _fib(_n - 2, memo)
                return memo[_n]
            return _fib(n)

.. code-block:: python

    >>> print(Calc.fib(7))
    8
    >>> print(Calc.fib(8))
    13
    >>> print(Calc.fib(6))
    21
    >>> print(Calc.fib(50))
    2586269025