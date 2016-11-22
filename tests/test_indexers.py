# -*- coding: utf-8 -*-

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from django.test import TestCase
from rest_search import get_elasticsearch

from tests.indexers import BookIndexer
from tests.models import Book, Tag


class IndexersTest(TestCase):
    def setUp(self):
        tags = [Tag.objects.create(slug=slug) for slug in ['foo', 'bar']]
        book = Book.objects.create(id=1, title='Some book')
        book.tags.set(tags)

    @patch('elasticsearch.client.indices.IndicesClient.create')
    @patch('rest_search.indexers.scan')
    def test_iterate_book_items(self, mock_scan, mock_create):
        es = get_elasticsearch()
        indexer = BookIndexer()
        with self.assertNumQueries(3):
            data = list(indexer.iterate_items(es))
        self.assertEqual(data, [
            {
                '_id': 1,
                '_index': 'bogus',
                '_source': {
                    'id': 1,
                    'tags': ['foo', 'bar'],
                    'title': 'Some book',
                },
                '_type': 'Book',
            }
        ])
