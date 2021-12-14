# -*- coding: utf-8 -*-

from unittest.mock import patch

from django.test import TestCase

from rest_search.tasks import create_index, delete_index, patch_index, update_index
from tests.models import Book, Tag


class MockBulk(object):
    def __init__(self):
        self.actions = []

    def __call__(self, es, actions, raise_on_error=True):
        self.actions.extend(actions)


class TasksTest(TestCase):
    def setUp(self):
        tags = [Tag.objects.create(slug=slug) for slug in ["foo", "bar"]]
        book = Book.objects.create(id=1, title="Some book")
        book.tags.set(tags)

    @patch("elasticsearch.client.indices.IndicesClient.exists")
    @patch("elasticsearch.client.indices.IndicesClient.create")
    def test_create_index(self, mock_create, mock_exists):
        mock_exists.return_value = False

        create_index()
        mock_exists.assert_called_once_with("book")
        mock_create.assert_called_once_with(
            index="book",
            body={
                "mappings": {"properties": {"tags": {"type": "keyword"}}},
                "settings": {
                    "analysis": {
                        "analyzer": {
                            "default": {
                                "tokenizer": "standard",
                                "filter": ["lowercase", "asciifolding"],
                            }
                        }
                    }
                },
            },
        )

    @patch("elasticsearch.client.indices.IndicesClient.exists")
    @patch("elasticsearch.client.indices.IndicesClient.create")
    def test_create_index_exists(self, mock_create, mock_exists):
        mock_exists.return_value = True

        create_index()
        mock_exists.assert_called_once_with("book")
        mock_create.assert_not_called()

    @patch("elasticsearch.client.indices.IndicesClient.delete")
    def test_delete_index(self, mock_delete):
        delete_index()
        mock_delete.assert_called_once_with(index="book", ignore=404)

    @patch("rest_search.tasks.bulk")
    def test_patch_index(self, mock_bulk):
        mock_bulk.side_effect = MockBulk()

        patch_index({"Book": [1]})
        self.assertEqual(
            mock_bulk.side_effect.actions,
            [
                {
                    "_id": 1,
                    "_index": "book",
                    "_source": {"id": 1, "tags": ["foo", "bar"], "title": "Some book"},
                }
            ],
        )

    @patch("rest_search.tasks.bulk")
    def test_patch_index_only_delete(self, mock_bulk):
        mock_bulk.side_effect = MockBulk()

        patch_index({"Book": [2]})
        self.assertEqual(
            mock_bulk.side_effect.actions,
            [{"_id": 2, "_index": "book", "_op_type": "delete"}],
        )

    @patch("rest_search.tasks.bulk")
    def test_patch_index_with_delete(self, mock_bulk):
        mock_bulk.side_effect = MockBulk()

        patch_index({"Book": [1, 2]})
        self.assertEqual(
            mock_bulk.side_effect.actions,
            [
                {
                    "_id": 1,
                    "_index": "book",
                    "_source": {"id": 1, "tags": ["foo", "bar"], "title": "Some book"},
                },
                {"_id": 2, "_index": "book", "_op_type": "delete"},
            ],
        )

    @patch("rest_search.tasks.create_index")
    @patch("rest_search.indexers.scan")
    @patch("rest_search.tasks.bulk")
    def test_update_index(self, mock_bulk, mock_scan, mock_create_index):
        mock_bulk.side_effect = MockBulk()

        # nothing in index
        mock_scan.return_value = []
        update_index()
        mock_create_index.assert_called_once_with()

        self.assertEqual(
            mock_bulk.side_effect.actions,
            [
                {
                    "_id": 1,
                    "_index": "book",
                    "_source": {"id": 1, "tags": ["foo", "bar"], "title": "Some book"},
                }
            ],
        )

    @patch("rest_search.tasks.create_index")
    @patch("rest_search.indexers.scan")
    @patch("rest_search.tasks.bulk")
    def test_update_index_no_delete(self, mock_bulk, mock_scan, mock_create_index):
        mock_bulk.side_effect = MockBulk()

        # books : 1 (still there), 1001 (gone)
        mock_scan.return_value = [
            {"_id": "1", "_index": "book", "_score": 0.0},
            {"_id": "1001", "_index": "book", "_score": 0.0},
        ]
        update_index(remove=False)
        mock_create_index.assert_called_once_with()

        self.assertEqual(
            mock_bulk.side_effect.actions,
            [
                {
                    "_id": 1,
                    "_index": "book",
                    "_source": {"id": 1, "tags": ["foo", "bar"], "title": "Some book"},
                }
            ],
        )

    @patch("rest_search.tasks.create_index")
    @patch("rest_search.indexers.scan")
    @patch("rest_search.tasks.bulk")
    def test_update_index_with_deleted(self, mock_bulk, mock_scan, mock_create_index):
        mock_bulk.side_effect = MockBulk()

        # books : 1 (still there), 1001 (gone)
        mock_scan.return_value = [
            {"_id": "1", "_index": "book", "_score": 0.0},
            {"_id": "1001", "_index": "book", "_score": 0.0},
        ]
        update_index()
        mock_create_index.assert_called_once_with()

        self.assertEqual(
            mock_bulk.side_effect.actions,
            [
                {
                    "_id": 1,
                    "_index": "book",
                    "_source": {"id": 1, "tags": ["foo", "bar"], "title": "Some book"},
                },
                {"_id": 1001, "_index": "book", "_op_type": "delete"},
            ],
        )
