# -*- coding: utf-8 -*-

from django import forms


class SearchMixin(object):
    """
    Mixin to help build ElasticSearch queries.
    """
    def get_query(self):
        """
        Returns the query to be executed by ElasticSearch.
        """
        return self._score_query(self._build_query())

    def _build_query(self):
        query = {
            'bool': {}
        }

        for kind in ['filter', 'must', 'must_not', 'should']:
            clauses = getattr(self, 'get_%s_clauses' % kind)()
            if clauses:
                query['bool'][kind] = clauses

        if query['bool']:
            return query
        else:
            return {
                'match_all': {}
            }

    def get_filter_clauses(self):
        return []

    def get_must_clauses(self):
        return []

    def get_must_not_clauses(self):
        return []

    def get_should_clauses(self):
        return []

    def _score_query(self, query):
        return query


class SearchForm(SearchMixin, forms.Form):
    """
    Base form for building ElasticSearch queries.
    """
    def __init__(self, data, context={}):
        self.context = context
        super(SearchForm, self).__init__(data)
