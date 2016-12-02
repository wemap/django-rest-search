# -*- coding: utf-8 -*-

from django.test import TestCase

from tests.utils import patch


class MiddlewareTest(TestCase):
    @patch('rest_search.tasks.patch_index.delay')
    def test_empty(self, mock_delay):
        response = self.client.post('/books', {
            'title': 'New book',
        })
        self.assertEqual(response.status_code, 201)
