# -*- coding: utf-8 -*-

from django.test import TestCase
from rest_search import connections
from rest_search.tasks import (create_index, delete_index, patch_index,
                               update_index)
from tests.models import Book, Tag
from tests.utils import patch


class TasksTest(TestCase):
    def setUp(self):
        tags = [Tag.objects.create(slug=slug) for slug in ['foo', 'bar']]
        book = Book.objects.create(id=1, title='Some book')
        book.tags.set(tags)

    @patch('elasticsearch.client.indices.IndicesClient.exists')
    @patch('elasticsearch.client.indices.IndicesClient.create')
    def test_create_index(self, mock_create, mock_exists):
        mock_exists.return_value = False

        create_index()
        mock_exists.assert_called_once_with('bogus')
        mock_create.assert_called_once_with(
            index='bogus',
            body={
                'mappings': {
                    'Book': {
                        'properties': {
                            'tags': {
                                'index': 'not_analyzed',
                                'type': 'string',
                            }
                        }
                    }
                },
                'settings': {
                    'analysis': {
                        'analyzer': {
                            'default': {
                                'tokenizer': 'standard',
                                'filter': [
                                    'standard',
                                    'lowercase',
                                    'asciifolding',
                                ]
                            },
                        }
                    }
                }
            }
        )

    @patch('elasticsearch.client.indices.IndicesClient.exists')
    @patch('elasticsearch.client.indices.IndicesClient.create')
    def test_create_index_exists(self, mock_create, mock_exists):
        mock_exists.return_value = True

        create_index()
        mock_exists.assert_called_once_with('bogus')
        mock_create.assert_not_called()

    @patch('elasticsearch.client.indices.IndicesClient.delete')
    def test_delete_index(self, mock_delete):
        delete_index(connections['default'])
        mock_delete.assert_called_once_with(
            index='bogus',
            ignore=404
        )

    @patch('rest_search.tasks.bulk')
    def test_patch_index(self, mock_bulk):
        patch_index({
            'Book': [1],
        })
        self.assertEqual(len(mock_bulk.call_args_list), 1)
        operations = list(mock_bulk.call_args_list[0][0][1])
        self.assertEqual(operations, [
            {
                '_id': 1,
                '_index': 'bogus',
                '_source': {
                    'id': 1,
                    'tags': ['foo', 'bar'],
                    'title': 'Some book'
                },
                '_type': 'Book'
            }
        ])

    @patch('rest_search.tasks.bulk')
    def test_patch_index_only_delete(self, mock_bulk):
        patch_index({
            'Book': [2],
        })
        self.assertEqual(len(mock_bulk.call_args_list), 1)
        operations = list(mock_bulk.call_args_list[0][0][1])
        self.assertEqual(operations, [
            {
                '_id': 2,
                '_index': 'bogus',
                '_op_type': 'delete',
                '_type': 'Book',
            }
        ])

    @patch('rest_search.tasks.bulk')
    def test_patch_index_with_delete(self, mock_bulk):
        patch_index({
            'Book': [1, 2],
        })
        self.assertEqual(len(mock_bulk.call_args_list), 1)
        operations = list(mock_bulk.call_args_list[0][0][1])
        self.assertEqual(operations, [
            {
                '_id': 1,
                '_index': 'bogus',
                '_source': {
                    'id': 1,
                    'tags': ['foo', 'bar'],
                    'title': 'Some book'
                },
                '_type': 'Book'
            },
            {
                '_id': 2,
                '_index': 'bogus',
                '_op_type': 'delete',
                '_type': 'Book',
            }
        ])

    @patch('rest_search.tasks.create_index')
    @patch('rest_search.indexers.scan')
    @patch('rest_search.tasks.bulk')
    def test_update_index(self, mock_bulk, mock_scan, mock_create_index):
        # nothing in index
        mock_scan.return_value = []
        update_index()
        mock_create_index.assert_called_once_with()

        self.assertEqual(len(mock_bulk.call_args_list), 1)
        operations = list(mock_bulk.call_args_list[0][0][1])
        self.assertEqual(operations, [
            {
                '_id': 1,
                '_index': 'bogus',
                '_source': {
                    'id': 1,
                    'tags': ['foo', 'bar'],
                    'title': 'Some book'
                },
                '_type': 'Book'
            }
        ])


    @patch('rest_search.tasks.create_index')
    @patch('rest_search.indexers.scan')
    @patch('rest_search.tasks.bulk')
    def test_update_index_with_deleted(self, mock_bulk, mock_scan, mock_create_index):
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
        update_index()
        mock_create_index.assert_called_once_with()

        self.assertEqual(len(mock_bulk.call_args_list), 1)
        operations = list(mock_bulk.call_args_list[0][0][1])
        self.assertEqual(operations, [
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
