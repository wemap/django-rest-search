# -*- coding: utf-8 -*-

import certifi
from aws_requests_auth.aws_auth import AWSRequestsAuth
from django.conf import settings
from elasticsearch import Elasticsearch, RequestsHttpConnection


QUEUES = {}


def get_elasticsearch():
    host = settings.REST_SEARCH['HOST']

    kwargs = {
        'host': host,
        'port': settings.REST_SEARCH.get('PORT', 9200),
        'use_ssl': settings.REST_SEARCH.get('USE_SSL', False),
        'verify_certs': True,
        'ca_certs': certifi.where()
    }

    if 'AWS_ACCESS_KEY' in settings.REST_SEARCH and \
       'AWS_SECRET_KEY' in settings.REST_SEARCH and \
       'AWS_REGION' in settings.REST_SEARCH:

        kwargs['connection_class'] = RequestsHttpConnection
        kwargs['http_auth'] = AWSRequestsAuth(
            aws_access_key=settings.REST_SEARCH['AWS_ACCESS_KEY'],
            aws_secret_access_key=settings.REST_SEARCH['AWS_SECRET_KEY'],
            aws_host=host,
            aws_region=settings.REST_SEARCH['AWS_REGION'],
            aws_service='es')

    return Elasticsearch(**kwargs)


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
