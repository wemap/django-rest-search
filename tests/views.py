# -*- coding: utf-8 -*-

from rest_framework import viewsets

from rest_search.views import SearchAPIView
from tests.forms import BookSearchForm
from tests.indexers import BookIndexer
from tests.models import Author, Book
from tests.serializers import AuthorSerializer, BookSerializer


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class BookSearch(SearchAPIView):
    form_class = BookSearchForm
    indexer_class = BookIndexer


class BookSearchSorted(SearchAPIView):
    form_class = BookSearchForm
    indexer_class = BookIndexer

    def get_sort(self):
        return [{"id": {"order": "desc"}}]
