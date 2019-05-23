# -*- coding: utf-8 -*-

from unittest.mock import patch

from django.test import TestCase, override_settings

from rest_search import connections


class ConnectionTest(TestCase):
    def tearDown(self):
        del connections["default"]

    @override_settings(
        REST_SEARCH_CONNECTIONS={
            "default": {
                "AWS_ACCESS_KEY": "some-access-key",
                "AWS_REGION": "some-region",
                "AWS_SECRET_KEY": "some-secret-key",
                "HOST": "es.example.com",
            }
        }
    )
    @patch("rest_search.Elasticsearch")
    def test_aws_auth(self, mock_elasticsearch):
        es = connections["default"]
        self.assertIsNotNone(es)

        self.assertEqual(mock_elasticsearch.call_count, 1)
        self.assertEqual(mock_elasticsearch.call_args[0], ())
        self.assertEqual(
            sorted(mock_elasticsearch.call_args[1].keys()),
            ["connection_class", "host", "http_auth", "port", "use_ssl"],
        )

    @patch("rest_search.Elasticsearch")
    def test_no_auth(self, mock_elasticsearch):
        es = connections["default"]
        self.assertIsNotNone(es)

        self.assertEqual(mock_elasticsearch.call_count, 1)
        self.assertEqual(mock_elasticsearch.call_args[0], ())
        self.assertEqual(
            sorted(mock_elasticsearch.call_args[1].keys()), ["host", "port", "use_ssl"]
        )
