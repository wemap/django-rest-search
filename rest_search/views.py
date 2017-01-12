# -*- coding: utf-8 -*-

from rest_framework.exceptions import ValidationError
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.views import APIView


class SearchAPIView(APIView):
    def get(self, request, *args, **kwargs):
        query = self.get_query()

        pagination = LimitOffsetPagination()
        pagination.default_limit = 20
        pagination.limit = pagination.get_limit(request)
        pagination.offset = pagination.get_offset(request)
        pagination.request = request

        # execute elasticsearch query
        indexer = self.get_indexer()
        res = indexer.search(body={
            'query': query,
            'size': pagination.limit,
            'from': pagination.offset
        })

        # map back to expected format
        items = list(indexer.map_results(res['hits']['hits']))
        pagination.count = res['hits']['total']
        return pagination.get_paginated_response(items)

    def get_indexer(self):
        return self.indexer_class()

    def get_query(self):
        form = self.form_class(self.request.GET, context={
            'request': self.request
        })
        if not form.is_valid():
            raise ValidationError(form.errors)
        return form.get_query()
