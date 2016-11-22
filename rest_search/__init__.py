# -*- coding: utf-8 -*-

import certifi
from aws_requests_auth.aws_auth import AWSRequestsAuth
from django.conf import settings
from elasticsearch import Elasticsearch, RequestsHttpConnection


INDEXER_CLASSES = []
QUEUES = {}


def get_elasticsearch():
    host = settings.REST_SEARCH['HOST']

    auth = AWSRequestsAuth(
        aws_access_key=settings.REST_SEARCH['AWS_ACCESS_KEY'],
        aws_secret_access_key=settings.REST_SEARCH['AWS_SECRET_KEY'],
        aws_host=host,
        aws_region=settings.REST_SEARCH['AWS_REGION'],
        aws_service='es')

    return Elasticsearch(
        host=host,
        port=443,
        connection_class=RequestsHttpConnection,
        http_auth=auth,
        use_ssl=True,
        verify_certs=True,
        ca_certs=certifi.where(),
    )


def get_indexers():
    """
    Returns instances of all registered indexers.
    """
    return [cls() for cls in INDEXER_CLASSES]


def register_indexer(indexer_class):
    """
    Register an indexer class.
    """
    INDEXER_CLASSES.append(indexer_class)


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
        from rest_search.tasks import index_partial
        if getattr(settings, 'SEARCH_UPDATES_ENABLED', True):
            index_partial.delay(QUEUES)
        QUEUES = {}
