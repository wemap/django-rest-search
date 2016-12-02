# -*- coding: utf-8 -*-

from django.test import TestCase
from rest_search.decorators import flush_updates

from tests.models import Book
from tests.utils import patch


class DecoratorsTest(TestCase):
    @patch('rest_search.tasks.patch_index.delay')
    def test_flush_updates(self, mock_delay):
        @flush_updates
        def create_book():
            return Book.objects.create(title='Some book')

        create_book()
        mock_delay.assert_called_with({'Book': [1]})
