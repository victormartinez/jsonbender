from itertools import chain
from warnings import warn

from jsonbender.core import Bender


class ListOp(Bender):
    """
    Base class for operations on lists.
    Subclasses must implement the op() method, which takes the function passed
    to the operator's __init__(), a list of *values* and should return the
    desired result.
    """
    def __init__(self, *args):
        if len(args) == 1:
            self._func = args[0]
            self._bender = None
        # TODO: this is here for compatibility reasons.
        elif len(args) == 2:
            self._bender, self._func = args
            msg = ('Passing a bender to {0} is deprecated.'
                   'Please use {0} in a composition chain '
                   '(see docs for more details).'
                   .format(type(self).__name__))
            warn(DeprecationWarning(msg))
        else:
            msg = ('{} constructor only takes one parameter, {} given'
                   .format(type(self).__name__, len(args)))
            raise TypeError(msg)

    def op(self, func, vals):
        raise NotImplementedError()

    def execute(self, source):
        # TODO: this is here for compatibility reasons
        if self._bender:
            source = self._bender(source)
        return self.op(self._func, source)


class Forall(ListOp):
    """
    Builds a new list by applying the given function to each element of the
    selected list. Similar to Python's map().
    """
    op = map


class Reduce(ListOp):
    """
    Reduces a list into a single value by repeatedly applying the given
    function to the elements.
    The function must accept two parameters: the first is the accumulator (the
    value returned from the last call), which defaults to the first element of
    the list (hence, the list must be nonempty); the second is the next value fro the list.

    Example: To sum a given list,
        Reduce(K([1, 4, 6], lambda acc, i: acc+i) -> 11
    """
    def op(self, func, vals):
        try:
            return reduce(func, vals)
        except TypeError as e:  # empty list with no initial value
            raise ValueError(e.message)


class Filter(ListOp):
    """
    Builds a new list with the elements of the selected list for which the
    given function returns True. Similar to Python's filter().
    """
    op = filter


class FlatForall(ListOp):
    """
    Similar to Forall, but the given function must return a list for each
    element of the selected list, which are than "flattened" into a single
    list.

    Example: FlatForall(K([1, 10, 100]), lambda x: [x-1, x+1]) ->
             [[0, 2], [9, 11], [99, 101]] ->
             [0, 1, 9, 11, 99, 101]
    """
    def op(self, func, vals):
        return list(chain.from_iterable(map(func, vals)))
