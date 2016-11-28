# -*- coding: utf-8 -*-

from django import forms


class SearchForm(forms.Form):
    """
    Base form for building ElasticSearch queries.
    """
    def __init__(self, data, context={}):
        self.context = context
        super(SearchForm, self).__init__(data)

    def get_query(self):
        """
        Returns the query to be executed by ElasticSearch.
        """
        return self._score_query(self._build_query())

    def _build_query(self):
        filters = self.get_filter_clauses()
        musts = self.get_must_clauses()

        if musts:
            query = {
                'bool': {
                    'must': musts
                }
            }
            if filters:
                query['bool']['filter'] = filters
        elif filters:
            if len(filters) == 1:
                filter_q = filters[0]
            else:
                filter_q = {
                    'bool': {
                        'must': filters
                    }
                }
            query = {
                'constant_score': {
                    'filter': filter_q
                }
            }
        else:
            query = {
                'match_all': {}
            }

        return query

    def get_filter_clauses(self):
        return []

    def get_must_clauses(self):
        return []

    def _score_query(self, query):
        return query
