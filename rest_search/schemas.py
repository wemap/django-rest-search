# -*- coding: utf-8 -*-

import coreapi
import coreschema
from django import forms


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
    if isinstance(field, forms.BooleanField):
        field_class = coreschema.Boolean
    elif isinstance(field, forms.FloatField):
        field_class = coreschema.Number
    elif isinstance(field, (forms.IntegerField, forms.ModelChoiceField)):
        field_class = coreschema.Integer
    else:
        field_class = coreschema.String
    return field_class(description=field.help_text)
