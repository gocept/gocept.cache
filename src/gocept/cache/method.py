# Copyright (c) 2007 gocept gmbh & co. kg
# See also LICENSE.txt
# $Id$

import inspect
import time

import decorator


_caches = {}
_timeouts = {}


def collect():
    """Clear cache of results which have timed out"""
    for func in _caches:
        cache = {}
        for key in _caches[func]:
            if (time.time() - _caches[func][key][1] <
                _timeouts[func]):
                cache[key] = _caches[func][key]
        _caches[func] = cache


def clear():
    _caches.clear()
    _timeouts.clear()


def Memoize(timeout, ignore_self=False, _caches=_caches, _timeouts=_timeouts):
    """Memoize With Timeout

    Based on http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/325905

    """

    @decorator.decorator
    def func(f, *args, **kwargs):
        cache = _caches.setdefault(f, {})
        _timeouts.setdefault(f, timeout)

        cache_args = args
        if ignore_self:
            arguments = inspect.getargspec(f)[0]
            if arguments and arguments[0] == 'self':
                cache_args = args[1:]

        kw = kwargs.items()
        kw.sort()
        key = (cache_args, tuple(kw))

        try:
            hash(key)
        except TypeError:
            # Not hashable.
            key = None

        try:
            value, cached_time = cache[key]
            #print "cache"
            if (time.time() - cached_time) > timeout:
                raise KeyError
        except KeyError:
            #print "new"
            value = f(*args,**kwargs)
            if key is not None:
                cache[key] = (value, time.time())
        return value

    return func