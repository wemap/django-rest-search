# -*- coding: utf-8 -*-

from threading import local

import certifi
from aws_requests_auth.aws_auth import AWSRequestsAuth
from django.conf import settings
from elasticsearch import Elasticsearch, RequestsHttpConnection


DEFAULT_INDEX_SETTINGS = {
    'analysis': {
        'analyzer': {
            'default': {
                'tokenizer': 'standard',
                'filter': [
                    'standard',
                    'lowercase',
                    'asciifolding',
                ]
            }
        }
    }
}
QUEUES = {}


class ConnectionHandler(object):
    def __init__(self):
        self._connections = local()

    def __delitem__(self, alias):
        delattr(self._connections, alias)

    def __getitem__(self, alias):
        if hasattr(self._connections, alias):
            return getattr(self._connections, alias)

        conn = self.__create_connection(
            settings.REST_SEARCH_CONNECTIONS[alias])
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

        es = Elasticsearch(**kwargs)
        es._index = config['INDEX_NAME']
        es._settings = config.get('INDEX_SETTINGS', DEFAULT_INDEX_SETTINGS)
        return es


def get_elasticsearch(indexer=None):
    return connections['default']


def queue_add(updates):
    """
    Adds items to the updates queue, in the form:

    {
        'Book': [1, 2],
    }
    """
    if getattr(settings, 'SEARCH_UPDATES_ENABLED', True):
        for doc_type, pks in updates.items():
            if doc_type in QUEUES:
                QUEUES[doc_type].update(set(pks))
            else:
                QUEUES[doc_type] = set(pks)


def queue_flush():
    """
    Triggers a celery task for the queued updates, if any.
    """
    global QUEUES
    if QUEUES:
        from rest_search.tasks import patch_index
        # convert sets to lists, otherwise they are not JSON-serializable
        args = {}
        for doc_type, pks in QUEUES.items():
            args[doc_type] = list(pks)
        patch_index.delay(args)
        QUEUES.clear()


connections = ConnectionHandler()
