# -*- coding: utf-8 -*-

import uuid
from unittest.mock import patch

from django.test import TestCase

from rest_search.decorators import flush_updates
from tests.models import Author, Book


class DecoratorsTest(TestCase):
    @patch("rest_search.tasks.patch_index.delay")
    def test_flush_updates_author(self, mock_delay):
        @flush_updates
        def create_author():
            return Author.objects.create(
                name="Some author", pk=uuid.UUID("a5df7423-2ed3-452b-b13e-c643d3f4e85d")
            )

        create_author()
        mock_delay.assert_called_with(
            {"Author": ["a5df7423-2ed3-452b-b13e-c643d3f4e85d"]}
        )

    @patch("rest_search.tasks.patch_index.delay")
    def test_flush_updates_book(self, mock_delay):
        @flush_updates
        def create_book():
            return Book.objects.create(pk=1, title="Some book")

        create_book()
        mock_delay.assert_called_with({"Book": ["1"]})
