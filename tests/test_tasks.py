# -*- coding: utf-8 -*-

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from django.test import TestCase
from rest_search.tasks import patch_index, update_index

from tests.models import Book


class TasksTest(TestCase):
    def setUp(self):
        Book.objects.create(id=1, title='Some book')

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
                },
                'mappings': {
                    'Book': {
                        'properties': {
                            'tags': {
                                'type': 'string',
                                'index': 'not_analyzed',
                            }
                        }
                    }
                }
            },
            ignore=400
        )
        self.assertEqual(len(mock_bulk.call_args_list), 1)
