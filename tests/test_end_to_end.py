import time

from celery import Celery
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from rest_search.decorators import flush_updates
from rest_search.tasks import create_index, delete_index
from tests.models import Tag

app = Celery()
app.config_from_object("tests.celeryconfig")


@override_settings(
    REST_SEARCH_CONNECTIONS={
        "default": {
            "HOST": "localhost",
        }
    },
)
class EndToEndTest(TestCase):
    client_class = APIClient

    def setUp(self):
        create_index()

        Tag.objects.create(slug="foo")
        Tag.objects.create(slug="bar")
        Tag.objects.create(slug="qux")

    def tearDown(self):
        delete_index()

    @flush_updates
    def test_book(self):
        # Create books.
        response = self.client.post(
            "/books", {"tags": ["foo", "bar"], "title": "Some book"}
        )
        self.assertEqual(response.status_code, 201)
        book_pk = response.data["id"]

        response = self.client.post("/books", {"tags": ["qux"], "title": "Other book"})
        self.assertEqual(response.status_code, 201)

        # Allow time for indexing.
        time.sleep(1)

        # Search books.
        response = self.client.get("/books/search")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            {
                "count": 2,
                "next": None,
                "previous": None,
                "results": [
                    {"tags": ["foo", "bar"], "title": "Some book"},
                    {"tags": ["qux"], "title": "Other book"},
                ],
            },
        )

        response = self.client.get("/books/search", {"tags": "foo"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            {
                "count": 1,
                "next": None,
                "previous": None,
                "results": [{"tags": ["foo", "bar"], "title": "Some book"}],
            },
        )

        # Update book.
        response = self.client.put(
            f"/books/{book_pk}", {"tags": ["foo"], "title": "Some book (changed)"}
        )
        self.assertEqual(response.status_code, 200)

        # Allow time for indexing.
        time.sleep(1)

        # Search books.
        response = self.client.get("/books/search")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            {
                "count": 2,
                "next": None,
                "previous": None,
                "results": [
                    {"tags": ["qux"], "title": "Other book"},
                    {"tags": ["foo"], "title": "Some book (changed)"},
                ],
            },
        )

        # Delete book.
        response = self.client.delete(f"/books/{book_pk}")
        self.assertEqual(response.status_code, 204)

        # Allow time for indexing.
        time.sleep(1)

        # Search books.
        response = self.client.get("/books/search")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            {
                "count": 1,
                "next": None,
                "previous": None,
                "results": [
                    {"tags": ["qux"], "title": "Other book"},
                ],
            },
        )
