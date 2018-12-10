# -*- coding: utf-8 -*-

from django.utils.deprecation import MiddlewareMixin

from rest_search import queue_flush


class FlushUpdatesMiddleware(MiddlewareMixin):
    """
    Middleware that flushes ElasticSearch updates.
    """
    def process_response(self, request, response):
        queue_flush()
        return response
