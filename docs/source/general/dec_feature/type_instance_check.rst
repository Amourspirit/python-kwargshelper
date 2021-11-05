type_instance_check
===================

Many ``type`` validation decorators supports *optoinal* ``type_instance_check`` bool option.

True
----

When ``type_instance_check`` is ``True`` then if type does not match then an instance check will also be done.

.. code-block:: python

    from pathlib import Path
    from kwhelp.decorator import AcceptedTypes

    @AcceptedTypes(Path, type_instance_check=True)
    def is_file_exist(arg):
        return True

.. code-block:: python

    >>> p = Path("home", "user")
    >>> print(is_file_exist(arg=p))
    True

False
-----

.. code-block:: python

    from pathlib import Path
    from kwhelp.decorator import AcceptedTypes

    @AcceptedTypes(Path, type_instance_check=False)
    def is_file_exist(arg):
        return True

.. code-block:: python

    >>> p = Path("home", "user")
    >>> print(is_file_exist(arg=p))
    TypeError: Arg 'arg' in 1st position is expected to be of '<class 'pathlib.Path'>' but got 'PosixPath'

Explanation
-----------

In some cases such as **Mulitple Inheritance** type check may not pass

In the following example type check for ``str`` is ``True`` however, ``Path`` is false.

.. code-block:: python

    >>> from pathlib import Path
    >>> s = ""
    >>> print(type(s) is str)
    True
    >>> p = Path("home", "user")
    >>> print(type(p) is Path)
    False

In the following example instance check for ``Path`` is ``True``

.. code-block:: python

    >>> from pathlib import Path
    >>> p = Path("home", "user")
    >>> print(isinstance(p, Path))
    False