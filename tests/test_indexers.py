# -*- coding: utf-8 -*-

from unittest.mock import patch

from django.test import TestCase

from tests.indexers import BookIndexer, UnsupportedIndexer
from tests.models import Book, Tag


class IndexersTest(TestCase):
    def setUp(self):
        tags = [Tag.objects.create(slug=slug) for slug in ["foo", "bar"]]
        book = Book.objects.create(id=1, title="Some book")
        book.tags.set(tags)

    def test_map_results(self):
        indexer = BookIndexer()
        data = list(
            indexer.map_results(
                [
                    {
                        "_id": "1",
                        "_index": "book",
                        "_score": 0.0,
                        "_source": {
                            "id": 1,
                            "tags": ["foo", "bar"],
                            "title": "Some book",
                        },
                        "_type": "Book",
                    },
                    {
                        "_id": "2",
                        "_index": "book",
                        "_score": 0.0,
                        "_source": {"id": 2, "tags": [], "title": "Other book"},
                        "_type": "Book",
                    },
                ]
            )
        )
        self.assertEqual(
            data,
            [
                {"tags": ["foo", "bar"], "title": "Some book"},
                {"tags": [], "title": "Other book"},
            ],
        )

    @patch("rest_search.indexers.scan")
    def test_scan(self, mock_scan):
        mock_scan.return_value = [
            {"_id": "1", "_index": "book", "_score": 0.0, "_type": "Book"}
        ]

        indexer = BookIndexer()
        indexer.scan(body={"query": {"match_all": {}}})

    @patch("elasticsearch.client.Elasticsearch.search")
    def test_search(self, mock_search):
        mock_search.return_value = {
            "_shards": {"failed": 0, "successful": 5, "total": 5},
            "hits": {"hits": [], "max_score": None, "total": 0},
            "timed_out": False,
            "took": 6,
        }

        indexer = BookIndexer()
        indexer.search(body={"query": {"match_all": {}}})

    def test_unsupported_primary_key(self):
        with self.assertRaises(AssertionError) as cm:
            UnsupportedIndexer()
        self.assertEqual(
            str(cm.exception),
            "Unhandled primary key type <class 'django.db.models.fields.URLField'>",
        )
