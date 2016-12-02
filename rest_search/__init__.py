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
        'port': 443,
        'use_ssl': True,
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


def get_indexers():
    """
    Returns instances of all registered indexers.
    """
    return [cls() for cls in INDEXER_CLASSES]


def queue_update(sender, instance, **kwargs):
    """
    Queue an update to the elasticsearch index.
    """
    doc_type = instance.__class__.__name__
    if doc_type not in QUEUES:
        QUEUES[doc_type] = set()
    QUEUES[doc_type].add(instance.pk)


def queue_flush():
    """
    Triggers a celery task for the queued updates, if any.
    """
    global QUEUES
    if QUEUES:
        from rest_search.tasks import patch_index
        if getattr(settings, 'SEARCH_UPDATES_ENABLED', True):
            patch_index.delay(QUEUES)
        QUEUES = {}
