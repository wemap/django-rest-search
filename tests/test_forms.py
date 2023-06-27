# -*- coding: utf-8 -*-

from django.test import TestCase

from rest_search.forms import SearchForm
from tests.forms import BookSearchForm


class FormsTest(TestCase):
    def test_base(self):
        form = SearchForm({})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.get_query(), {"match_all": {}})

    def test_empty(self):
        form = BookSearchForm({})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.get_query(), {"match_all": {}})

    def test_with_id(self):
        form = BookSearchForm({"id": 1})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.get_query(), {"bool": {"filter": [{"term": {"id": 1}}]}})

    def test_with_query(self):
        form = BookSearchForm({"query": "foo"})
        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.get_query(),
            {
                "bool": {
                    "must": [
                        {"simple_query_string": {"fields": ["name"], "query": "foo"}}
                    ]
                }
            },
        )

    def test_with_tags(self):
        form = BookSearchForm({"tags": "tag1,tag2"})
        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.get_query(),
            {
                "bool": {
                    "filter": [{"term": {"tags": "tag1"}}, {"term": {"tags": "tag2"}}]
                }
            },
        )

    def test_with_tags_and_query(self):
        form = BookSearchForm({"query": "foo", "tags": "tag1,tag2"})
        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.get_query(),
            {
                "bool": {
                    "filter": [{"term": {"tags": "tag1"}}, {"term": {"tags": "tag2"}}],
                    "must": [
                        {"simple_query_string": {"fields": ["name"], "query": "foo"}}
                    ],
                }
            },
        )
