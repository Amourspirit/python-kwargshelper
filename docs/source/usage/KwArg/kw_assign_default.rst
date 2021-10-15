Kw_assign Default Value
=======================

Default value can be assigned by adding ``default`` args to :py:meth:`~.KwArg.kw_assign` method.

In the following ``msg`` arg is assigned a default of ``Result:``

.. include:: /source/inc/ex/KwArg_basic.rst

Method result contains prefix of ``msg`` default value

.. code-block:: python

    >>> result = my_method(first=10, second=22, end="!")
    >>> print(result)
    Result: 32!

Method result contains ``Tally`` as ``msg`` default is now overridden by assiging value.

.. code-block:: python

    >>> result = my_method(first=10, second=22, end="!", msg="Tally")
    >>> print(result)
    Tally 32!

Method will raise an error as ``msg`` must be of type ``str`` as defined by ``types``

.. code-block:: python

    >>> result = my_method(first=10, second=22, end="!", msg=-34)
    TypeError: KwArg arg 'msg' is expected to be of '<class 'str'>' but got 'int'