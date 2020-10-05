# -*- coding: utf-8 -*-

from rest_framework.exceptions import ValidationError
from rest_framework.filters import BaseFilterBackend
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.views import APIView

from rest_search.schemas import get_form_schema, get_form_schema_operation_parameters


class SearchFilterBackend(BaseFilterBackend):
    """
    Dummy filter backend to enable API documentation.
    """

    def get_schema_fields(self, view):
        return get_form_schema(view.form_class)

    def get_schema_operation_parameters(self, view):
        return get_form_schema_operation_parameters(view.form_class)


class SearchAPIView(APIView):
    filter_backends = (SearchFilterBackend,)

    def _get_total(self, total):
        if isinstance(total, dict):
            # for ES >= 7
            # hits.total is now an object in the search response
            return total["value"]
        else:
            # for ES < 7
            return total

    def get(self, request, *args, **kwargs):
        query = self.get_query()
        sort = self.get_sort()

        pagination = LimitOffsetPagination()
        pagination.default_limit = 20
        pagination.limit = pagination.get_limit(request)
        pagination.offset = pagination.get_offset(request)
        pagination.request = request

        body = {
            "track_total_hits": True,
            "query": query,
            "size": pagination.limit,
            "from": pagination.offset,
        }
        if sort:
            body["sort"] = sort

        # execute elasticsearch query
        indexer = self.get_indexer()
        res = indexer.search(body=body)

        # map back to expected format
        items = list(indexer.map_results(res["hits"]["hits"]))
        pagination.count = self._get_total(res["hits"]["total"])
        return pagination.get_paginated_response(items)

    def get_indexer(self):
        return self.indexer_class()

    def get_query(self):
        """
        Returns the 'query' element of the ElasticSearch request body.
        """
        form = self.form_class(self.request.GET, context={"request": self.request})
        if not form.is_valid():
            raise ValidationError(form.errors)
        return form.get_query()

    def get_sort(self):
        """
        Returns the 'sort' element of the ElastiSearch request body.

        To use the default sorting (by score) return None.
        """
        return None
