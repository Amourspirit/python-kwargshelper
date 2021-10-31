TypeCheckKw Usage
=================

:py:class:`~.decorator.TypeCheckKw` decorator allows each arg of a function match one of the rules specified.
Each arg can have seperate rules applied.

:py:class:`~.decorator.TypeCheckKw` constructor args ``arg_info`` and ``rules``  work together.
``arg_info`` is a dictionary with a key of ``str`` that matches an arg name of the function that
is being decorated.
``arg_info`` value is one of the following:

    * ``int`` is an index of an item in ``rules``
    *  ``type`` a type to match

``arg_info`` can be :ref:`mixed <mixed-arg_info>`.

``types`` is a list of type to match.

Example Usage
-------------

:py:class:`~.decorator.TypeCheckKw` decorated function.

.. code-block:: python

    from kwhelp.decorator import TypeCheckKw

    @TypeCheckKw(arg_info={"speed": 0, "limit": 0, "hours": 0, "name": 1},
                    types=[(int, float), str])
    def speed_msg(speed, limit, **kwargs) -> str:
        name = kwargs.get('name', 'You')
        if limit > speed:
            msg = f"Current speed is '{speed}'. {name} may go faster as the limit is '{limit}'."
        elif speed == limit:
            msg = f"Current speed is '{speed}'. {name} are at the limit."
        else:
            msg = f"Please slow down limit is '{limit}' and current speed is '{speed}'."
        if 'hours' in kwargs:
            msg = msg + f" Current driving hours is '{kwargs['hours']}'."
        return msg

.. code-block:: python

    >>> result = speed_msg(speed=45, limit=60)
    >>> print(result)
    Current speed is '45'. You may go faster as the limit is '60'.

.. code-block:: python

    >>> result = speed_msg(speed=45, limit=60, name="John")
    >>> print(result)
    Current speed is '45'. John may go faster as the limit is '60'.

If types fail validation then a ``TypeError`` is raised.

.. code-block:: python

    >>> result = speed_msg(speed=-2, limit=60, name=17, hours=5)
    TypeError: Arg 'name' is expected to be of '<class 'str'>' but got 'int'

.. _mixed-arg_info:

``speed_msg`` decorated with a mixed ``arg_info`` with ``IRule`` instance and index to ``rules``.

.. code-block:: python

    from kwhelp.decorator import TypeCheckKw

    @TypeCheckKw(arg_info={"speed": 0, "limit": 0, "hours": 0, "name": str},
                    types=[(int, float)])
    def speed_msg(speed, limit, **kwargs) -> str:
        name = kwargs.get('name', 'You')
        if limit > speed:
            msg = f"Current speed is '{speed}'. {name} may go faster as the limit is '{limit}'."
        elif speed == limit:
            msg = f"Current speed is '{speed}'. {name} are at the limit."
        else:
            msg = f"Please slow down limit is '{limit}' and current speed is '{speed}'."
        if 'hours' in kwargs:
            msg = msg + f" Current driving hours is '{kwargs['hours']}'."
        return msg