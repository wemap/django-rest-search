# -*- coding: utf-8 -*-

import coreschema
from django import forms
from django.test import TestCase, override_settings
from rest_framework.schemas import coreapi, openapi

from rest_search.forms import SearchForm
from rest_search.schemas import (
    get_form_field_coreapi_schema,
    get_form_field_openapi_schema,
    get_form_schema,
    get_form_schema_operation_parameters,
)
from tests.forms import BookSearchForm


class FormFieldCoreapiSchemaTest(TestCase):
    def test_boolean(self):
        form_field = forms.BooleanField()
        core_field = get_form_field_coreapi_schema(form_field)
        self.assertTrue(isinstance(core_field, coreschema.Boolean))

    def test_datetime(self):
        form_field = forms.DateTimeField()
        core_field = get_form_field_coreapi_schema(form_field)
        self.assertTrue(isinstance(core_field, coreschema.String))
        self.assertEqual(core_field.format, "date-time")

    def test_char(self):
        form_field = forms.CharField()
        core_field = get_form_field_coreapi_schema(form_field)
        self.assertTrue(isinstance(core_field, coreschema.String))

    def test_float(self):
        form_field = forms.FloatField()
        core_field = get_form_field_coreapi_schema(form_field)
        self.assertTrue(isinstance(core_field, coreschema.Number))
        self.assertFalse(core_field.integer_only)

    def test_integer(self):
        form_field = forms.IntegerField()
        core_field = get_form_field_coreapi_schema(form_field)
        self.assertTrue(isinstance(core_field, coreschema.Integer))
        self.assertTrue(core_field.integer_only)


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
    def test_base_coreapi(self):
        fields = get_form_schema(SearchForm)
        self.assertEqual(fields, [])

    def test_base_openapi(self):
        fields = get_form_schema_operation_parameters(SearchForm)
        self.assertEqual(fields, [])

    def test_book_coreapi(self):
        fields = get_form_schema(BookSearchForm)
        self.assertEqual(len(fields), 3)
        self.assertEqual(fields[0].name, "id")
        self.assertEqual(fields[1].name, "query")
        self.assertEqual(fields[2].name, "tags")

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
    @override_settings(
        REST_FRAMEWORK={
            "DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.coreapi.AutoSchema"
        }
    )
    def test_coreapi(self):
        generator = coreapi.SchemaGenerator()
        schema = generator.get_schema()
        self.assertTrue("books" in schema)
        self.assertTrue("search" in schema["books"])
        self.assertTrue("list" in schema["books"]["search"])

        fields = schema["books"]["search"]["list"].fields
        self.assertEqual(len(fields), 3)
        self.assertEqual(fields[0].name, "id")
        self.assertEqual(fields[1].name, "query")
        self.assertEqual(fields[2].name, "tags")

    @override_settings(
        REST_FRAMEWORK={
            "DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.openapi.AutoSchema"
        }
    )
    def test_openapi(self):
        generator = openapi.SchemaGenerator()
        schema = generator.get_schema()
        self.assertTrue("/books/search" in schema["paths"])

        parameters = schema["paths"]["/books/search"]["get"]["parameters"]
        self.assertEqual(len(parameters), 3)
        self.assertEqual(parameters[0]["name"], "id")
        self.assertEqual(parameters[1]["name"], "query")
        self.assertEqual(parameters[2]["name"], "tags")
