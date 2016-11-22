# -*- coding: utf-8 -*-

try:
    from unittest.mock import patch
except ImportError:
    from mock import patch

from django.test import TestCase
from rest_search.tasks import index_data, index_partial

from tests.models import Book


class TasksTest(TestCase):
    def setUp(self):
        Book.objects.create(id=1, title='Some book')

    @patch('elasticsearch.client.indices.IndicesClient.create')
    @patch('rest_search.tasks.bulk')
    def test_index_data(self, mock_bulk, mock_create):
        index_data()
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

    @patch('rest_search.tasks.bulk')
    def test_index_partial(self, mock_bulk):
        index_partial({
            'Book': [1],
        })
        self.assertEqual(len(mock_bulk.call_args_list), 1)
