# -*- coding: utf-8 -*-

import coreapi
import coreschema
from django import forms
from django.utils.encoding import force_text


def get_form_schema(form_class):
    """
    Return the coreapi schema for the given form class.
    """
    fields = []
    for name, field in form_class.declared_fields.items():
        fields.append(coreapi.Field(
            location='query',
            name=name,
            required=field.required,
            schema=get_form_field_schema(field)))
    return fields


def get_form_field_schema(field):
    """
    Returns the coreapi schema for the given form field.
    """
    title = force_text(field.label) if field.label else ''
    description = force_text(field.help_text) if field.help_text else ''

    if isinstance(field, forms.BooleanField):
        field_class = coreschema.Boolean
    elif isinstance(field, forms.FloatField):
        field_class = coreschema.Number
    elif isinstance(field, (forms.IntegerField, forms.ModelChoiceField)):
        field_class = coreschema.Integer
    else:
        field_class = coreschema.String

    return field_class(description=description, title=title)
