# -*- coding: utf-8 -*-

import coreschema
from django import forms
from django.test import TestCase
from rest_framework.schemas import SchemaGenerator
from rest_search.forms import SearchForm
from rest_search.schemas import get_form_field_schema, get_form_schema

from tests.forms import BookSearchForm


class FormFieldSchemaTest(TestCase):
    def test_boolean(self):
        form_field = forms.BooleanField()
        core_field = get_form_field_schema(form_field)
        self.assertTrue(isinstance(core_field, coreschema.Boolean))

    def test_char(self):
        form_field = forms.CharField()
        core_field = get_form_field_schema(form_field)
        self.assertTrue(isinstance(core_field, coreschema.String))

    def test_float(self):
        form_field = forms.FloatField()
        core_field = get_form_field_schema(form_field)
        self.assertTrue(isinstance(core_field, coreschema.Number))
        self.assertFalse(core_field.integer_only)

    def test_integer(self):
        form_field = forms.IntegerField()
        core_field = get_form_field_schema(form_field)
        self.assertTrue(isinstance(core_field, coreschema.Integer))
        self.assertTrue(core_field.integer_only)


class FormSchemaTest(TestCase):
    def test_base(self):
        fields = get_form_schema(SearchForm)
        self.assertEqual(fields, [])

    def test_book(self):
        fields = get_form_schema(BookSearchForm)
        self.assertEqual(len(fields), 3)
        self.assertEqual(fields[0].name, 'id')
        self.assertEqual(fields[1].name, 'query')
        self.assertEqual(fields[2].name, 'tags')


class SchemaGeneratorTest(TestCase):
    def test_schema(self):
        generator = SchemaGenerator()
        schema = generator.get_schema()
        self.assertTrue('books' in schema)
        self.assertTrue('search' in schema['books'])
        self.assertTrue('list' in schema['books']['search'])

        fields = schema['books']['search']['list'].fields
        self.assertEqual(len(fields), 3)
        self.assertEqual(fields[0].name, 'id')
        self.assertEqual(fields[1].name, 'query')
        self.assertEqual(fields[2].name, 'tags')
