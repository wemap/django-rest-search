# -*- coding: utf-8 -*-

from django.test import TestCase
from rest_search import connections
from rest_search.tasks import (create_index, delete_index, patch_index,
                               update_index)
from tests.models import Book
from tests.utils import patch


class TasksTest(TestCase):
    def setUp(self):
        Book.objects.create(id=1, title='Some book')

    @patch('elasticsearch.client.indices.IndicesClient.create')
    def test_create_index(self, mock_create):
        create_index()
        mock_create.assert_called_with(
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

    @patch('elasticsearch.client.indices.IndicesClient.delete')
    def test_delete_index(self, mock_delete):
        delete_index(connections['default'])
        mock_delete.assert_called_with(
            index='bogus',
            ignore=404
        )

    @patch('rest_search.tasks.bulk')
    def test_patch_index(self, mock_bulk):
        patch_index({
            'Book': [1],
        })
        self.assertEqual(len(mock_bulk.call_args_list), 1)

    @patch('elasticsearch.client.indices.IndicesClient.create')
    @patch('rest_search.tasks.bulk')
    def test_update_index(self, mock_bulk, mock_create):
        update_index()
        mock_create.assert_called_with(
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

        self.assertEqual(len(mock_bulk.call_args_list), 1)
