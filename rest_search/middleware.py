# -*- coding: utf-8 -*-

from rest_search import queue_flush


class FlushUpdatesMiddleware(object):
    """
    Middleware that flushes ElasticSearch updates.
    """
    def process_response(self, request, response):
        queue_flush()
        return response
