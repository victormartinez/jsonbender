from jsonbender.core import Bender


class K(Bender):
    """
    Selects a constant value.
    """
    def __init__(self, value):
        self._val = value

    def execute(self, source):
        return self._val


class S(Bender):
    """
    Selects a path of keys.
    Example:
        S('a', 0, 'b').execute({'a': [{'b': 42}]}) -> 42
    """
    def __init__(self, *path):
        if not path:
            raise ValueError('No path given')
        self._path = path

    def execute(self, source):
        for key in self._path:
            source = source[key]
        return source


class F(Bender):
    """
    Lifts a python callable into a Bender, so it can be composed.
    The extra positional and named parameters are passed to the function at
    bending time after the given value.

    `func` is a callable

    Example:
    ```
    f = F(sorted, key=lambda d: d['id'])
    K([{'id': 3}, {'id': 1}]) >> f  #  -> [{'id': 1}, {'id': 3}]
    ```
    """
    def __init__(self, func, *args, **kwargs):
        self._func = func
        self._args = args
        self._kwargs = kwargs

    def execute(self, value):
        return self._func(value, *self._args, **self._kwargs)

