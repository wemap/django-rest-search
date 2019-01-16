# -*- coding: utf-8 -*-

import logging

from celery import shared_task
from elasticsearch.helpers import bulk

from rest_search import get_elasticsearch
from rest_search.indexers import _get_registered, bulk_iterate

logger = logging.getLogger('rest_search')


def create_index():
    """
    Creates the ElasticSearch index if it does not exist.
    """
    conns = {}
    for indexer in _get_registered():
        es = get_elasticsearch(indexer)
        key = (es, indexer.index)
        if key not in conns:
            conns[key] = {
                'mappings': {},
                'settings': es._settings
            }
        if indexer.mappings is not None:
            mappings = conns[key]['mappings']
            mappings[indexer.doc_type] = indexer.mappings

    for (es, index), body in conns.items():
        if not es.indices.exists(index):
            es.indices.create(index=index, body=body)


def delete_index():
    """
    Deletes the ElasticSearch index.
    """
    for indexer in _get_registered():
        es = get_elasticsearch(indexer)
        es.indices.delete(index=indexer.index, ignore=404)


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


def _delete_items(indexer, pks):
    es = get_elasticsearch(indexer)

    def mapper(pk):
        return {
            '_index': indexer.index,
            '_type': indexer.doc_type,
            '_id': pk,
            '_op_type': 'delete',
        }

    bulk(es, map(mapper, pks), raise_on_error=False)


def _index_items(indexer, queryset):
    es = get_elasticsearch(indexer)
    seen_pks = set()

    def mapper(item):
        seen_pks.add(item.pk)
        return {
            '_index': indexer.index,
            '_type': indexer.doc_type,
            '_id': item.pk,
            '_source': indexer.serializer_class(item).data
        }

    bulk(es, map(mapper, bulk_iterate(queryset)))
    return seen_pks


def _patch_index(indexer, pks):
    # index current items
    queryset = indexer.get_queryset().filter(pk__in=pks)
    seen_pks = _index_items(indexer, queryset)

    # remove obsolete items
    removed_pks = set(pks) - seen_pks
    _delete_items(indexer, removed_pks)


def _update_index(indexer, remove):
    scan = indexer.scan(query={'stored_fields': []})
    old_pks = set([int(i['_id']) for i in scan])

    # index current items
    queryset = indexer.get_queryset()
    seen_pks = _index_items(indexer, queryset)

    # remove obsolete items
    if remove:
        removed_pks = old_pks - seen_pks
        _delete_items(indexer, removed_pks)
