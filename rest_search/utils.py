# -*- coding: utf-8 -*-

from threading import local

import certifi
from aws_requests_auth.aws_auth import AWSRequestsAuth
from django.conf import settings
from elasticsearch import Elasticsearch, RequestsHttpConnection


class ConnectionHandler(object):
    def __init__(self):
        self._connections = local()

    def __delitem__(self, alias):
        delattr(self._connections, alias)

    def __getitem__(self, alias):
        if hasattr(self._connections, alias):
            return getattr(self._connections, alias)

        assert alias == 'default'
        conn = self.__create_connection(settings.REST_SEARCH)
        setattr(self._connections, alias, conn)
        return conn

    def __create_connection(self, config):
        kwargs = {
            'host': config['HOST'],
            'port': config.get('PORT', 9200),
            'use_ssl': config.get('USE_SSL', False),
            'verify_certs': True,
            'ca_certs': certifi.where()
        }

        if 'AWS_ACCESS_KEY' in config and \
           'AWS_SECRET_KEY' in config and \
           'AWS_REGION' in config:

            kwargs['connection_class'] = RequestsHttpConnection
            kwargs['http_auth'] = AWSRequestsAuth(
                aws_access_key=config['AWS_ACCESS_KEY'],
                aws_secret_access_key=config['AWS_SECRET_KEY'],
                aws_host=config['HOST'],
                aws_region=config['AWS_REGION'],
                aws_service='es')

        return Elasticsearch(**kwargs)


class ConnectionRouter(object):
    pass
