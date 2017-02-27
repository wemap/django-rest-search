# -*- coding: utf-8 -*-

from rest_framework.exceptions import ValidationError
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.views import APIView


class SearchAPIView(APIView):
    def get(self, request, *args, **kwargs):
        query = self.get_query()
        sort = self.get_sort()

        pagination = LimitOffsetPagination()
        pagination.default_limit = 20
        pagination.limit = pagination.get_limit(request)
        pagination.offset = pagination.get_offset(request)
        pagination.request = request

        body = {
            'query': query,
            'size': pagination.limit,
            'from': pagination.offset
        }
        if sort:
            body['sort'] = sort

        # execute elasticsearch query
        indexer = self.get_indexer()
        res = indexer.search(body=body)

        # map back to expected format
        items = list(indexer.map_results(res['hits']['hits']))
        pagination.count = res['hits']['total']
        return pagination.get_paginated_response(items)

    def get_indexer(self):
        return self.indexer_class()

    def get_query(self):
        """
        Returns the 'query' element of the ElasticSearch request body.
        """
        form = self.form_class(self.request.GET, context={
            'request': self.request
        })
        if not form.is_valid():
            raise ValidationError(form.errors)
        return form.get_query()

    def get_sort(self):
        """
        Returns the 'sort' element of the ElastiSearch request body.

        To use the default sorting (by score) return None.
        """
        return None
