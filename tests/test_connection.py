# -*- coding: utf-8 -*-

from unittest.mock import Mock, patch

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
    @patch("rest_search.OpenSearch")
    def test_aws_auth(self, mock_opensearch):
        es = connections["default"]
        self.assertIsNotNone(es)

        self.assertEqual(mock_opensearch.call_count, 1)
        self.assertEqual(mock_opensearch.call_args[0], ())
        self.assertEqual(
            sorted(mock_opensearch.call_args[1].keys()),
            ["connection_class", "host", "http_auth", "port", "use_ssl"],
        )

    @override_settings(
        REST_SEARCH_CONNECTIONS={
            "default": {
                "AWS_REGION": "some-region",
                "HOST": "es.example.com",
            }
        }
    )
    @patch("rest_search.OpenSearch")
    @patch("rest_search.Session")
    def test_aws_role_auth(self, mock_session, mock_opensearch):
        mock_creds = Mock(
            access_key="mock-access-key",
            secret_key="mock-secret-key",
            token="mock-token",
        )
        mock_session.return_value.get_credentials.return_value.get_frozen_credentials.return_value = mock_creds

        es = connections["default"]
        self.assertIsNotNone(es)

        self.assertEqual(mock_opensearch.call_count, 1)
        self.assertEqual(mock_opensearch.call_args[0], ())
        self.assertEqual(
            sorted(mock_opensearch.call_args[1].keys()),
            ["connection_class", "host", "http_auth", "port", "use_ssl"],
        )

    @patch("rest_search.OpenSearch")
    def test_no_auth(self, mock_opensearch):
        es = connections["default"]
        self.assertIsNotNone(es)

        self.assertEqual(mock_opensearch.call_count, 1)
        self.assertEqual(mock_opensearch.call_args[0], ())
        self.assertEqual(
            sorted(mock_opensearch.call_args[1].keys()), ["host", "port", "use_ssl"]
        )
