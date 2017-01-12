# -*- coding: utf-8 -*-

from django.test import TestCase

from tests.indexers import BookIndexer
from tests.models import Book, Tag
from tests.utils import patch


class IndexersTest(TestCase):
    def setUp(self):
        tags = [Tag.objects.create(slug=slug) for slug in ['foo', 'bar']]
        book = Book.objects.create(id=1, title='Some book')
        book.tags.set(tags)

    @patch('rest_search.indexers.scan')
    def test_iterate_items(self, mock_scan):
        indexer = BookIndexer()
        with self.assertNumQueries(3):
            data = list(indexer.iterate_items())
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

    @patch('rest_search.indexers.scan')
    def test_iterate_items_with_deleted(self, mock_scan):
        # books : 1 (still there), 1001 (gone)
        mock_scan.return_value = [
            {
                '_id': '1',
                '_index': 'bogus',
                '_score': 0.0,
                '_type': 'Book'
            },
            {
                '_id': '1001',
                '_index': 'bogus',
                '_score': 0.0,
                '_type': 'Book'
            },
        ]

        indexer = BookIndexer()
        with self.assertNumQueries(3):
            data = list(indexer.iterate_items())
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
            },
            {
                '_id': 1001,
                '_index': 'bogus',
                '_op_type': 'delete',
                '_type': 'Book',
            }
        ])

    def test_map_results(self):
        indexer = BookIndexer()
        data = list(indexer.map_results([
            {
                '_id': '1',
                '_index': 'bogus',
                '_score': 0.0,
                '_source': {
                    'id': 1,
                    'tags': ['foo', 'bar'],
                    'title': 'Some book',
                },
                '_type': 'Book'
            },
            {
                '_id': '2',
                '_index': 'bogus',
                '_score': 0.0,
                '_source': {
                    'id': 2,
                    'tags': [],
                    'title': 'Other book',
                },
                '_type': 'Book'
            },
        ]))
        self.assertEqual(data, [
            {
                'tags': ['foo', 'bar'],
                'title': 'Some book',
            },
            {
                'tags': [],
                'title': 'Other book',
            }
        ])

    def test_partial_items(self):
        indexer = BookIndexer()
        with self.assertNumQueries(3):
            data = list(indexer.partial_items([1, 2]))

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
            },
            {
                '_id': 2,
                '_index': 'bogus',
                '_op_type': 'delete',
                '_type': 'Book',
            }
        ])

    @patch('rest_search.indexers.scan')
    def test_scan(self, mock_scan):
        mock_scan.return_value = [
            {
                '_id': '1',
                '_index': 'bogus',
                '_score': 0.0,
                '_type': 'Book'
            }
        ]

        indexer = BookIndexer()
        indexer.scan(body={
            'query': {
                'match_all': {}
            }
        })

    @patch('elasticsearch.client.Elasticsearch.search')
    def test_search(self, mock_search):
        mock_search.return_value = {
            "_shards": {
                "failed": 0,
                "successful": 5,
                "total": 5
            },
            "hits": {
                "hits": [],
                "max_score": None,
                "total": 0
            },
            "timed_out": False,
            "took": 6
        }

        indexer = BookIndexer()
        indexer.search(body={
            'query': {
                'match_all': {}
            }
        })
