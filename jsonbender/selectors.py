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

    def optional(self, default=None):
        """
        Return an OptS with the same path and with the given `default`.
        """
        return OptS(*self._path, default=default)


class OptS(S):
    """
    Similar to S. However, if any of the keys doesn't exist, returns the
    `default` value.

    `default` defaults to None.
    Example:
        OptS('a', 0, 'b', default=23).execute({'a': []}) -> 23
    """

    def __init__(self, *path, **kwargs):
        self.default = kwargs.get('default')
        super(OptS, self).__init__(*path)

    def execute(self, source):
        try:
            ret = super(OptS, self).execute(source)
        except KeyError:
            return self.default
        else:
            return ret


class F(Bender):
    def __init__(self, func, *args, **kwargs):
        self._func = func
        self._args = args
        self._kwargs = kwargs

    def execute(self, value):
        return self._func(value, *self._args, **self._kwargs)

