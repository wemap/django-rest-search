# -*- coding: utf-8 -*-

from django import forms
from django.utils.encoding import force_str


def get_form_schema_operation_parameters(form_class):
    """
    Return the openapi schema for the given form class.
    """
    fields = []
    for name, field in form_class.declared_fields.items():
        fields.append(
            {
                "name": name,
                "required": field.required,
                "in": "query",
                "description": force_str(field.help_text) if field.help_text else "",
                "schema": get_form_field_openapi_schema(field),
            }
        )
    return fields


def get_form_field_openapi_schema(field):
    if isinstance(field, forms.BooleanField):
        return {"type": "boolean"}
    elif isinstance(field, forms.DateField):
        return {"type": "string", "format": "date"}
    elif isinstance(field, forms.DateTimeField):
        return {"type": "string", "format": "date-time"}
    elif isinstance(field, forms.FloatField):
        return {"type": "number"}
    elif isinstance(field, (forms.IntegerField, forms.ModelChoiceField)):
        return {"type": "integer"}
    else:
        return {"type": "string"}
