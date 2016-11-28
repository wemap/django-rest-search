# -*- coding: utf-8 -*-

from django import forms

from rest_search.forms import SearchForm


class BookSearchForm(SearchForm):
    query = forms.CharField(required=False)
    tags = forms.CharField(required=False)

    def get_filter_clauses(self):
        clauses = []

        if self.cleaned_data['tags']:
            for tag in self.cleaned_data['tags'].split(','):
                clauses.append({
                    'term': {
                        'tags': tag
                    }
                })

        return clauses

    def get_must_clauses(self):
        clauses = []

        if self.cleaned_data['query']:
            clauses.append({
                'simple_query_string': {
                    'fields': ['name'],
                    'query': self.cleaned_data['query'],
                }
            })

        return clauses
