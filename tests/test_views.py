# -*- coding: utf-8 -*-

from django.test import TestCase

from tests.utils import patch


class ViewsTest(TestCase):
    @patch('rest_search.tasks.patch_index.delay')
    def test_create(self, mock_delay):
        response = self.client.post('/books', {
            'title': 'New book',
        })
        self.assertEqual(response.status_code, 201)

    @patch('elasticsearch.client.Elasticsearch.search')
    def test_search(self, mock_search):
        mock_search.return_value = {
            "_shards": {
                "failed": 0,
                "successful": 5,
                "total": 5
            },
            "hits": {
                "hits": [
                    {
                        "_id": "1",
                        "_index": "bogus",
                        "_score": 1,
                        "_source": {
                            'id': 1,
                            'title': 'New book',
                        },
                        "_type": "Book"
                    }
                ],
                "max_score": 0.60911113,
                "total": 1
            },
            "timed_out": False,
            "took": 39
        }

        response = self.client.get('/books/search', {
            'title': 'New book',
        })
        self.assertEqual(response.status_code, 200)
