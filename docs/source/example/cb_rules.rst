Using Callbacks & Rules
=======================

Using rules with Callback:

**Example:**

.. code-block:: python
    :caption: Custom Class

    from kwhelp import KwargsHelper, AfterAssignEventArgs, BeforeAssignEventArgs, AssignBuilder
    import kwhelp.rules as rules

    class MyClass:
        def __init__(self, **kwargs):
            self._loop_count = -1
            kw = KwargsHelper(self, {**kwargs})
            ab = AssignBuilder()
            kw.add_handler_before_assign(self._arg_before_cb)
            kw.add_handler_after_assign(self._arg_after_cb)
            ab.append(key='exporter', rules=[rules.RuleStr])
            ab.append(key='name', require=True, rules=[rules.RuleStr],
                    default='unknown')
            ab.append(key='file_name', require=True, rules=[
                rules.RuleStr, rules.RuleStrNotNullOrEmpty])
            ab.append(key='loop_count', require=True, rules=[
                    rules.RuleInt, rules.RuleIntPositive],
                    default=self._loop_count)
            result = True
            # by default assign will raise errors if conditions are not met.
            for arg in ab:
                result = kw.assign_helper(arg)
                if result == False:
                    break
            if result == False:
                raise ValueError("Error parsing kwargs")

        def _arg_before_cb(self, helper: KwargsHelper,
                        args: BeforeAssignEventArgs) -> None:
            if args.key == 'name' and args.field_value == 'unknown':
                args.field_value = 'None'

        def _arg_after_cb(self, helper: KwargsHelper,
                        args: AfterAssignEventArgs) -> None:
            # callback function after value assigned to attribute
            if args.key == 'name' and args.field_value == 'unknown':
                raise ValueError(
                    f"{args.key} This should never happen. value was suppose to be reassigned")

        @property
        def exporter(self) -> str:
            return self._exporter

        @property
        def file_name(self) -> str:
            return self._file_name

        @property
        def name(self) -> str:
            return self._name

        @property
        def loop_count(self) -> int:
            return self._loop_count

.. code-block:: python
    :caption: Assignment

    >>> my_class = MyClass(exporter='json', file_name='data.json', loop_count=3)
    >>> print(my_class.exporter)
    json
    >>> print(my_class.file_name)
    data.json
    >>> print(my_class.name)
    None
    >>> print(my_class.loop_count)
    3

.. seealso::

    :doc:`KwargsHelper <../kwhelp/KwargsHelper>`,
    :doc:`AfterAssignEventArgs <../kwhelp/AfterAssignEventArgs>`,
    :doc:`BeforeAssignEventArgs <../kwhelp/BeforeAssignEventArgs>`,
    :doc:`AssignBuilder <../kwhelp/AssignBuilder>`,
    :doc:`Rules <../kwhelp/rules/index>`