# -*- coding: utf-8 -*-

from rest_search import indexers

from tests.models import Book
from tests.serializers import BookSerializer


class BookIndexer(indexers.Indexer):
    mappings = {
        'properties': {
            'tags': {
                'type': 'keyword',
            }
        }
    }
    private_properties = ['id']
    serializer_class = BookSerializer

    def get_queryset(self):
        return Book.objects.prefetch_related('tags')


indexers.register(BookIndexer)
