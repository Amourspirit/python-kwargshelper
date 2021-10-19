.. code-block:: python

    class MyClass:
        def __init__(self, **kwargs):
            self._msg = ''
            kw = KwargsHelper(self, {**kwargs})
            kw.assign(key='msg', require=True, types=['str'])
            kw.assign(key='length', types=['int'], default=-1)

        @property
        def msg(self) -> str:
            return self._msg

        @property
        def length(self) -> str:
            return self._length