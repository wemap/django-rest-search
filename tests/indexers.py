# -*- coding: utf-8 -*-

from rest_search import indexers
from tests.models import Author, Book
from tests.serializers import AuthorSerializer, BookSerializer


class AuthorIndexer(indexers.Indexer):
    serializer_class = AuthorSerializer

    def get_queryset(self):
        return Author.objects.all()


class BookIndexer(indexers.Indexer):
    mappings = {"properties": {"tags": {"type": "keyword"}}}
    private_properties = ["id"]
    serializer_class = BookSerializer

    def get_queryset(self):
        return Book.objects.prefetch_related("tags")


indexers.register(AuthorIndexer)
indexers.register(BookIndexer)
