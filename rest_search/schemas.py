# -*- coding: utf-8 -*-

from django import forms
from django.utils.encoding import force_str


def get_form_schema(form_class):
    """
    Return the coreapi schema for the given form class.
    """
    import coreapi

    fields = []
    for name, field in form_class.declared_fields.items():
        fields.append(
            coreapi.Field(
                location="query",
                name=name,
                required=field.required,
                schema=get_form_field_coreapi_schema(field),
            )
        )
    return fields


def get_form_field_coreapi_schema(field):
    """
    Returns the coreapi schema for the given form field.
    """
    import coreschema

    title = force_str(field.label) if field.label else ""
    description = force_str(field.help_text) if field.help_text else ""

    if isinstance(field, forms.BooleanField):
        field_class = coreschema.Boolean
    elif isinstance(field, forms.DateTimeField):
        return coreschema.String(
            description=description, title=title, format="date-time"
        )
    elif isinstance(field, forms.FloatField):
        field_class = coreschema.Number
    elif isinstance(field, (forms.IntegerField, forms.ModelChoiceField)):
        field_class = coreschema.Integer
    else:
        field_class = coreschema.String

    return field_class(description=description, title=title)


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
