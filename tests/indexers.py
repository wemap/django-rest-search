# -*- coding: utf-8 -*-

from rest_search import indexers, register_indexer

from tests.models import Book
from tests.serializers import BookSerializer


class BookIndexer(indexers.Indexer):
    index = 'bogus'
    mappings = {
        'properties': {
            'tags': {
                'type': 'string',
                'index': 'not_analyzed',
            }
        }
    }
    serializer_class = BookSerializer

    def get_queryset(self):
        return Book.objects.prefetch_related('tags')


register_indexer(BookIndexer)
