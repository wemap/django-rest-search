# -*- coding: utf-8 -*-

import uuid
from unittest import mock
from unittest.mock import patch

from django.test import TestCase

from rest_search.tasks import create_index, delete_index, patch_index, update_index
from tests.models import Author, Book, Tag


class MockBulk(object):
    def __init__(self):
        self.actions = []

    def __call__(self, es, actions, raise_on_error=True):
        self.actions.extend(actions)


class TasksTest(TestCase):
    maxDiff = None

    def create_authors(self):
        Author.objects.create(
            name="Some author",
            unique_id=uuid.UUID("4996decc-c8f0-4492-800a-023ee7aaeec5"),
        )

    def create_books(self):
        book = Book.objects.create(id=1, title="Some book")
        book.tags.set([Tag.objects.create(slug=slug) for slug in ["foo", "bar"]])

    @patch("elasticsearch.client.indices.IndicesClient.exists")
    @patch("elasticsearch.client.indices.IndicesClient.create")
    def test_create_index(self, mock_create, mock_exists):
        mock_exists.return_value = False

        create_index()

        self.assertEqual(
            mock_exists.mock_calls,
            [
                mock.call("author"),
                mock.call("book"),
            ],
        )
        self.assertEqual(
            mock_create.mock_calls,
            [
                mock.call(
                    index="author",
                    body={
                        "mappings": {},
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
                ),
                mock.call(
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
                ),
            ],
        )

    @patch("elasticsearch.client.indices.IndicesClient.exists")
    @patch("elasticsearch.client.indices.IndicesClient.create")
    def test_create_index_exists(self, mock_create, mock_exists):
        mock_exists.return_value = True

        create_index()

        self.assertEqual(
            mock_exists.mock_calls,
            [
                mock.call("author"),
                mock.call("book"),
            ],
        )
        mock_create.assert_not_called()

    @patch("elasticsearch.client.indices.IndicesClient.delete")
    def test_delete_index(self, mock_delete):
        delete_index()

        self.assertEqual(
            mock_delete.mock_calls,
            [
                mock.call(index="author", ignore=404),
                mock.call(index="book", ignore=404),
            ],
        )

    @patch("rest_search.tasks.bulk")
    def test_patch_index(self, mock_bulk):
        self.create_authors()
        self.create_books()

        mock_bulk.side_effect = MockBulk()

        patch_index(
            {
                "Author": ["4996decc-c8f0-4492-800a-023ee7aaeec5"],
                "Book": ["1"],
            }
        )

        self.assertEqual(
            mock_bulk.side_effect.actions,
            [
                {
                    "_id": "4996decc-c8f0-4492-800a-023ee7aaeec5",
                    "_index": "author",
                    "_source": {
                        "name": "Some author",
                        "unique_id": "4996decc-c8f0-4492-800a-023ee7aaeec5",
                    },
                },
                {
                    "_id": "1",
                    "_index": "book",
                    "_source": {"id": 1, "tags": ["foo", "bar"], "title": "Some book"},
                },
            ],
        )

    @patch("rest_search.tasks.bulk")
    def test_patch_index_only_delete(self, mock_bulk):
        self.create_authors()
        self.create_books()

        mock_bulk.side_effect = MockBulk()

        patch_index({"Book": ["2"]})
        self.assertEqual(
            mock_bulk.side_effect.actions,
            [{"_id": "2", "_index": "book", "_op_type": "delete"}],
        )

    @patch("rest_search.tasks.bulk")
    def test_patch_index_with_delete(self, mock_bulk):
        self.create_authors()
        self.create_books()

        mock_bulk.side_effect = MockBulk()

        patch_index({"Book": ["1", "2"]})

        self.assertEqual(
            mock_bulk.side_effect.actions,
            [
                {
                    "_id": "1",
                    "_index": "book",
                    "_source": {"id": 1, "tags": ["foo", "bar"], "title": "Some book"},
                },
                {"_id": "2", "_index": "book", "_op_type": "delete"},
            ],
        )

    @patch("rest_search.tasks.create_index")
    @patch("rest_search.tasks.bulk")
    def test_update_index(self, mock_bulk, mock_create_index):
        self.create_books()

        mock_bulk.side_effect = MockBulk()

        def mock_scan(_es, *, index, **kwargs):
            # nothing in index
            return []

        with patch("rest_search.indexers.scan", new=mock_scan):
            update_index()

        mock_create_index.assert_called_once_with()
        self.assertEqual(
            mock_bulk.side_effect.actions,
            [
                {
                    "_id": "1",
                    "_index": "book",
                    "_source": {"id": 1, "tags": ["foo", "bar"], "title": "Some book"},
                }
            ],
        )

    @patch("rest_search.tasks.create_index")
    @patch("rest_search.tasks.bulk")
    def test_update_index_no_delete(self, mock_bulk, mock_create_index):
        self.create_books()

        mock_bulk.side_effect = MockBulk()

        def mock_scan(_es, *, index, **kwargs):
            return {
                "author": [],
                "book": [
                    {"_id": "1", "_index": "book", "_score": 0.0},  # still in DB
                    {"_id": "1001", "_index": "book", "_score": 0.0},  # gone from DB
                ],
            }[index]

        with patch("rest_search.indexers.scan", new=mock_scan):
            update_index(remove=False)

        mock_create_index.assert_called_once_with()
        self.assertEqual(
            mock_bulk.side_effect.actions,
            [
                {
                    "_id": "1",
                    "_index": "book",
                    "_source": {"id": 1, "tags": ["foo", "bar"], "title": "Some book"},
                }
            ],
        )

    @patch("rest_search.tasks.create_index")
    @patch("rest_search.tasks.bulk")
    def test_update_index_with_deleted_author(self, mock_bulk, mock_create_index):
        self.create_authors()

        mock_bulk.side_effect = MockBulk()

        def mock_scan(_es, *, index, **kwargs):
            return {
                "author": [
                    {
                        "_id": "4996decc-c8f0-4492-800a-023ee7aaeec5",
                        "_index": "author",
                        "_source": {
                            "name": "Some author",
                            "unique_id": "4996decc-c8f0-4492-800a-023ee7aaeec5",
                        },
                    },  # still in DB
                    {
                        "_id": "8550d60b-a3a7-4f07-8587-0b1a05a97e65",
                        "_index": "author",
                        "_source": {
                            "name": "Some author",
                            "unique_id": "8550d60b-a3a7-4f07-8587-0b1a05a97e65",
                        },
                    },  # gone from DB
                ],
                "book": [],
            }[index]

        with patch("rest_search.indexers.scan", new=mock_scan):
            update_index()

        mock_create_index.assert_called_once_with()
        self.assertEqual(
            mock_bulk.side_effect.actions,
            [
                {
                    "_id": "4996decc-c8f0-4492-800a-023ee7aaeec5",
                    "_index": "author",
                    "_source": {
                        "name": "Some author",
                        "unique_id": "4996decc-c8f0-4492-800a-023ee7aaeec5",
                    },
                },
                {
                    "_id": "8550d60b-a3a7-4f07-8587-0b1a05a97e65",
                    "_index": "author",
                    "_op_type": "delete",
                },
            ],
        )

    @patch("rest_search.tasks.create_index")
    @patch("rest_search.tasks.bulk")
    def test_update_index_with_deleted_book(self, mock_bulk, mock_create_index):
        self.create_books()

        mock_bulk.side_effect = MockBulk()

        def mock_scan(_es, *, index, **kwargs):
            return {
                "author": [],
                "book": [
                    {"_id": "1", "_index": "book", "_score": 0.0},  # still in DB
                    {"_id": "1001", "_index": "book", "_score": 0.0},  # gone from DB
                ],
            }[index]

        with patch("rest_search.indexers.scan", new=mock_scan):
            update_index()

        mock_create_index.assert_called_once_with()
        self.assertEqual(
            mock_bulk.side_effect.actions,
            [
                {
                    "_id": "1",
                    "_index": "book",
                    "_source": {"id": 1, "tags": ["foo", "bar"], "title": "Some book"},
                },
                {"_id": "1001", "_index": "book", "_op_type": "delete"},
            ],
        )
