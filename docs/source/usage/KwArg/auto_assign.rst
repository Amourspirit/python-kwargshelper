Auto assign
===========

Auto assign of key, value parirs can be accomplish by calling
:py:meth:`.KwargsHelper.auto_assign` of :py:attr:`.KwArg.kwargs_helper` property.

.. code-block:: python

    from kwhelp import KwArg

    def sum_of(**kwargs) -> str:
        kw = KwArg(**kwargs)
        kw.kwargs_helper.auto_assign(types=[int])
        result = 0
        for key in kw.kwargs_helper.kw_args:
            result = result + kw.__dict__[key]
        return result

Assing values of type ``int``.

.. code-block:: python

    >>> result = sum_of(first_qtr=199, second_qtr=201)
    >>> print(result)
    400

Assigning value not of type ``int`` results in an error.

.. code-block:: python

    >>> result = sum_of(first_qtr=199.78, second_qtr=201)
    TypeError: KwArg arg 'first_qtr' is expected to be of '<class 'int'>' but got 'float'

.. seealso::

    * :py:attr:`.KwArg.kwargs_helper`
    * :doc:`KwargsHelper auto_assign Usage <../KwargsHelper/auto_assign>`