.. code-block:: python

    from kwhelp import KwargsHelper, AfterAssignEventArgs, BeforeAssignEventArgs, AssignBuilder

    class MyClass:
        def __init__(self, **kwargs):
            self._loop_count = -1
            kw = KwargsHelper(originator=self, obj_kwargs={**kwargs})
            ab = AssignBuilder()
            kw.add_handler_before_assign(self._arg_before_cb)
            kw.add_handler_after_assign(self._arg_after_cb)
            ab.append(key='exporter', require=True, types=[str])
            ab.append(key='name', require=True, types=[str],
                    default='unknown')
            ab.append(key='file_name', require=True, types=[str])
            ab.append(key='loop_count', types=[int],
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
            # callback function before value assigned to attribute
            if args.key == 'loop_count' and args.field_value < 0:
                # cancel will raise CancelEventError unless
                # KwargsHelper constructor has cancel_error=False
                args.cancel = True
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