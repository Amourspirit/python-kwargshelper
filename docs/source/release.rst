Release Notes
=============

Version 2.4.0
-------------

Added SubClass, SubClassKw decorators.

Added ``opt_all_args`` feature to ``AcceptedTypes`` decorator. See :doc:`/source/general/dec_feature/opt_all_args`

Update AcceptedTypes decorator. Now passing enum types into constructor no longer
require enum type to be passed in as iterable object.

Updated many decorator error message. Now they are a little more human readable.

Version 2.3.0
-------------

Added decorator ``ArgsMinMax``

Added Rules:

    * RuleIterable
    * RuleNotIterable

Added ``opt_return`` feature to many decorators. See :doc:`/source/general/dec_feature/opt_return`

Version 2.2.1
-------------

``ArgsLen`` decorator now allows zero length args.

.. code-block:: python

    @ArgsLen(0, 2)
    def foo(*args, **kwargs): pass

Version 2.2.0
-------------

Added Decorator ArgsLen.

Added Rules:

    * RuleByteSigned
    * RuleByteUnsigned

Version 2.1.4
-------------

Bug fix for ``AcceptedTypes`` Decorator when function has leading named args before positional args.

The following will now work.

.. code-block:: python

    @AcceptedTypes(float, str, int, [Color], int, bool)
    def myfunc(arg1, arg2, *args, opt=True): pass

Version 2.1.3
-------------

Update fix for python DeprecationWarning:
    Using or importing the ABCs from 'collections'
    instead of from 'collections.abc' is deprecated

Added Install documentation.

Added Development documentation.

Version 2.1.2
-------------

Fix for Decorator ``AcceptedTypes`` not working correctly with optional arguments.

Version 2.1.1
-------------

Fix for version 2.1.0 setup not building correctly.

Version 2.1.0
-------------

**New Features**

Added Decorators that provided a large range of options for validating function, class input and return values.
Also added decorators that provide other functionality such as singleton pattern.