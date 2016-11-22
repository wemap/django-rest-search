# -*- coding: utf-8 -*-

import functools

from rest_search import queue_flush


def flush_updates(function):
    """
    Decorator that flushes ElasticSearch updates.
    """
    @functools.wraps(function)
    def wrap(*args, **kwargs):
        try:
            return function(*args)
        finally:
            queue_flush()

    return wrap
