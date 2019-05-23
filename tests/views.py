# -*- coding: utf-8 -*-

from rest_framework.generics import CreateAPIView

from rest_search.views import SearchAPIView
from tests.forms import BookSearchForm
from tests.indexers import BookIndexer
from tests.serializers import BookSerializer


class BookCreate(CreateAPIView):
    serializer_class = BookSerializer


class BookSearch(SearchAPIView):
    form_class = BookSearchForm
    indexer_class = BookIndexer


class BookSearchSorted(SearchAPIView):
    form_class = BookSearchForm
    indexer_class = BookIndexer

    def get_sort(self):
        return [{"id": {"order": "desc"}}]
