# coding: utf-8
# region Event Args
from .. helper.builder import HelperArgs
class BeforeAssignEventArgs:
    def __init__(self, help_args: HelperArgs, originator: object):
        self._helper_args = help_args
        self._originator = originator
        self._field_name: str = ''
        self._field_value: object = None
        self._cancel = False
    # region Properties

    @property
    def field_name(self) -> str:
        '''The name of the field that value will be assigned'''
        return self._field_name

    @field_name.setter
    def field_name(self, value: str) -> None:
        self._field_name = str(value)

    @property
    def field_value(self) -> object:
        '''The value that will be assigned`field_name`'''
        return self._field_value

    @field_value.setter
    def field_value(self, value: object) -> None:
        self._field_value = value

    @property
    def key(self) -> str:
        '''Gets the key currently being read'''
        return self._helper_args.key

    @property
    def helper_args(self) -> HelperArgs:
        ''''Get the args used to for modify/creating attribute'''
        return self._helper_args

    @property
    def originator(self) -> object:
        '''Gets object that attributes assigned/modified for '''
        return self._originator

    @property
    def cancel(self) -> bool:
        return self._cancel

    @cancel.setter
    def cancel(self, value: bool) -> None:
        self._cancel = bool(value)
    # endregion Properties


class AfterAssignEventArgs:
    def __init__(self, help_args: HelperArgs, originator: object) -> None:
        self._helper_args = help_args
        self._field_name: str = ''
        self._field_value: object = None
        self._originator = originator
        self._rules_passed = True
        self._canceled = False
        self._success = False
    # region Properties

    @property
    def key(self) -> str:
        '''Gets the key currently being read'''
        return self._helper_args.key

    @property
    def field_name(self) -> str:
        '''The name of the field that value was assigned'''
        return self._field_name

    @property
    def field_value(self) -> object:
        '''The value that is assigned to `field_name`'''
        return self._field_value

    @property
    def helper_args(self) -> HelperArgs:
        ''''Get the args used to for modify/creating attribute'''
        return self._helper_args

    @property
    def originator(self) -> object:
        '''Gets object that attributes assigned/modified for '''
        return self._originator

    @property
    def rules_passed(self) -> bool:
        '''Get if all applied rules passed'''
        return self._rules_passed

    @property
    def canceled(self) -> bool:
        '''Get if assigment was canceled by before events'''
        return self._canceled

    @property
    def success(self) -> bool:
        '''Get assigning of attribue/value succeeded'''
        return self._success

    @success.setter
    def success(self, value: bool) -> None:
        '''Set assigning of attribue/value succeeded'''
        self._success = bool(value)
    # endregion Properties
# endregion Event Args
