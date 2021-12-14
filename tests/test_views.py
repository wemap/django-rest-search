# -*- coding: utf-8 -*-

from unittest.mock import patch

from django.test import TestCase


class ViewsTest(TestCase):
    @patch("rest_search.tasks.patch_index.delay")
    def test_create(self, mock_delay):
        response = self.client.post("/books", {"title": "New book"})
        self.assertEqual(response.status_code, 201)

    @patch("elasticsearch.client.Elasticsearch.search")
    def test_search(self, mock_search):
        mock_search.return_value = {
            "_shards": {"failed": 0, "successful": 5, "total": 5},
            "hits": {
                "hits": [
                    {
                        "_id": "1",
                        "_index": "book",
                        "_score": 1,
                        "_source": {
                            "id": 1,
                            "tags": ["foo", "bar"],
                            "title": "New book",
                        },
                    }
                ],
                "max_score": 0.60911113,
                "total": {"value": 1, "relation": "eq"},
            },
            "timed_out": False,
            "took": 39,
        }

        response = self.client.get("/books/search", {"title": "New book"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            {
                "count": 1,
                "next": None,
                "previous": None,
                "results": [{"tags": ["foo", "bar"], "title": "New book"}],
            },
        )

        mock_search.assert_called_once_with(
            body={
                "from": 0,
                "query": {"match_all": {}},
                "size": 20,
                "track_total_hits": True,
            },
            index="book",
        )

    def test_search_invalid(self):
        response = self.client.get("/books/search", {"id": "a"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {"id": ["Enter a whole number."]})

    @patch("elasticsearch.client.Elasticsearch.search")
    def test_search_pagination(self, mock_search):
        mock_search.return_value = {
            "_shards": {"failed": 0, "successful": 5, "total": 5},
            "hits": {
                "hits": [],
                "max_score": 0,
                "total": {"value": 1, "relation": "eq"},
            },
            "timed_out": False,
            "took": 24,
        }

        response = self.client.get(
            "/books/search", {"limit": 10, "offset": 1, "title": "New book"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            {
                "count": 1,
                "next": None,
                "previous": "http://testserver/books/search" "?limit=10&title=New+book",
                "results": [],
            },
        )

        mock_search.assert_called_once_with(
            body={
                "from": 1,
                "query": {"match_all": {}},
                "size": 10,
                "track_total_hits": True,
            },
            index="book",
        )

    @patch("elasticsearch.client.Elasticsearch.search")
    def test_search_sorted(self, mock_search):
        mock_search.return_value = {
            "_shards": {"failed": 0, "successful": 5, "total": 5},
            "hits": {
                "hits": [
                    {
                        "_id": "1",
                        "_index": "book",
                        "_score": 1,
                        "_source": {
                            "id": 1,
                            "tags": ["foo", "bar"],
                            "title": "New book",
                        },
                    }
                ],
                "max_score": 0.60911113,
                "total": {"value": 1, "relation": "eq"},
            },
            "timed_out": False,
            "took": 39,
        }

        response = self.client.get("/books/search_sorted", {"title": "New book"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data,
            {
                "count": 1,
                "next": None,
                "previous": None,
                "results": [{"tags": ["foo", "bar"], "title": "New book"}],
            },
        )

        mock_search.assert_called_once_with(
            body={
                "from": 0,
                "query": {"match_all": {}},
                "size": 20,
                "sort": [{"id": {"order": "desc"}}],
                "track_total_hits": True,
            },
            index="book",
        )
