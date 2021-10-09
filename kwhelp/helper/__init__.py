# coding: utf-8
class Singleton(type):
    """Singleton abstrace class"""
    _instances = {}
    # https://stackoverflow.com/questions/6760685/creating-a-singleton-in-python
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
class NoThing(metaclass=Singleton):
    '''Singleton Class to mimic null'''

NO_THING = NoThing()
"""
Singleton Class instance that represents null object.
"""
