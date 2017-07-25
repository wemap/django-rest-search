# -*- coding: utf-8 -*-

import logging

from celery import shared_task
from elasticsearch.helpers import bulk, scan

from rest_search import get_elasticsearch
from rest_search.indexers import bulk_iterate, _get_registered


logger = logging.getLogger('rest_search')


def create_index():
    """
    Creates the ElasticSearch index if it does not exist.
    """
    conns = {}
    for indexer in _get_registered():
        es = get_elasticsearch(indexer)
        if es not in conns:
            conns[es] = {
                'mappings': {},
                'settings': es._settings
            }
        if indexer.mappings is not None:
            mappings = conns[es]['mappings']
            mappings[indexer.doc_type] = indexer.mappings

    for es, body in conns.items():
        if not es.indices.exists(es._index):
            es.indices.create(index=es._index, body=body)


def delete_index(es):
    """
    Deletes the ElasticSearch index.
    """
    return es.indices.delete(index=es._index, ignore=404)


@shared_task
def patch_index(updates):
    """
    Performs a partial update of the ElasticSearch index.
    """
    updates_str = ['%s: %d items' % (k, len(v)) for k, v in updates.items()]
    logger.info('Patching index (%s)' % ', '.join(updates_str))

    indexers = _get_registered()
    for doc_type, pks in updates.items():
        for indexer in indexers:
            if indexer.doc_type == doc_type:
                _patch_index(indexer, pks)


@shared_task
def update_index(remove=True):
    """
    Performs a full update of the ElasticSearch index.
    """
    logger.info('Updating index')

    create_index()

    for indexer in _get_registered():
        _update_index(indexer, remove=remove)


def _index_item(item, indexer, index):
    return {
        '_index': index,
        '_type': indexer.doc_type,
        '_id': item.pk,
        '_source': indexer.serializer_class(item).data
    }


def _delete_item(pk, indexer, index):
    return {
        '_index': index,
        '_type': indexer.doc_type,
        '_id': pk,
        '_op_type': 'delete',
    }


def _patch_index(indexer, pks):
    es = get_elasticsearch(indexer)
    index = es._index
    queryset = indexer.get_queryset().filter(pk__in=pks)

    def generate():
        removed = set(pks)

        # index current items
        for item in bulk_iterate(queryset):
            removed.discard(item.pk)
            yield _index_item(item, indexer=indexer, index=index)

        # remove obsolete items
        for pk in removed:
            yield _delete_item(pk, indexer=indexer, index=index)

    bulk(es, generate())


def _update_index(indexer, remove):
    es = get_elasticsearch(indexer)
    index = es._index
    queryset = indexer.get_queryset()

    def generate():
        # index current items
        ids = set()
        for item in bulk_iterate(queryset):
            ids.add(item.pk)
            yield _index_item(item, indexer=indexer, index=index)

        # remove obsolete items
        if remove:
            for i in scan(es, index=index, doc_type=indexer.doc_type, query={'stored_fields': []}):
                pk = int(i['_id'])
                if pk not in ids:
                    yield _delete_item(pk, indexer=indexer, index=index)

    bulk(es, generate())
