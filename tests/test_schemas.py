# -*- coding: utf-8 -*-

from django import forms
from django.test import TestCase
from rest_framework.schemas import openapi

from rest_search.forms import SearchForm
from rest_search.schemas import (
    get_form_field_openapi_schema,
    get_form_schema_operation_parameters,
)
from tests.forms import BookSearchForm


class FormFieldOpenapiSchemaTest(TestCase):
    def test_boolean(self):
        form_field = forms.BooleanField()
        self.assertEqual(get_form_field_openapi_schema(form_field), {"type": "boolean"})

    def test_date(self):
        form_field = forms.DateField()
        self.assertEqual(
            get_form_field_openapi_schema(form_field),
            {"type": "string", "format": "date"},
        )

    def test_datetime(self):
        form_field = forms.DateTimeField()
        self.assertEqual(
            get_form_field_openapi_schema(form_field),
            {"type": "string", "format": "date-time"},
        )

    def test_char(self):
        form_field = forms.CharField()
        self.assertEqual(get_form_field_openapi_schema(form_field), {"type": "string"})

    def test_float(self):
        form_field = forms.FloatField()
        self.assertEqual(get_form_field_openapi_schema(form_field), {"type": "number"})

    def test_integer(self):
        form_field = forms.IntegerField()
        self.assertEqual(get_form_field_openapi_schema(form_field), {"type": "integer"})


class FormSchemaTest(TestCase):
    def test_base_openapi(self):
        fields = get_form_schema_operation_parameters(SearchForm)
        self.assertEqual(fields, [])

    def test_book_openapi(self):
        fields = get_form_schema_operation_parameters(BookSearchForm)
        self.assertEqual(
            fields,
            [
                {
                    "name": "id",
                    "required": False,
                    "in": "query",
                    "description": "",
                    "schema": {"type": "integer"},
                },
                {
                    "name": "query",
                    "required": False,
                    "in": "query",
                    "description": "A full-text search on the name.",
                    "schema": {"type": "string"},
                },
                {
                    "name": "tags",
                    "required": False,
                    "in": "query",
                    "description": "",
                    "schema": {"type": "string"},
                },
            ],
        )


class SchemaGeneratorTest(TestCase):
    def test_openapi(self):
        generator = openapi.SchemaGenerator()
        schema = generator.get_schema()
        self.assertTrue("/books/search" in schema["paths"])

        parameters = schema["paths"]["/books/search"]["get"]["parameters"]
        self.assertEqual(len(parameters), 3)
        self.assertEqual(parameters[0]["name"], "id")
        self.assertEqual(parameters[1]["name"], "query")
        self.assertEqual(parameters[2]["name"], "tags")
