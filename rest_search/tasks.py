# -*- coding: utf-8 -*-

import logging

from celery import shared_task
from elasticsearch.helpers import bulk

from rest_search import get_elasticsearch
from rest_search.indexers import _get_registered


logger = logging.getLogger('rest_search')


def create_index():
    conns = {}
    for indexer in _get_registered():
        es = get_elasticsearch(indexer)
        if es not in conns:
            conns[es] = {
                'mappings': {},
                'settings': {
                    'analysis': {
                        'analyzer': {
                            'default': {
                                'tokenizer': 'standard',
                                'filter': [
                                    'standard',
                                    'lowercase',
                                    'asciifolding',
                                ]
                            },
                        }
                    }
                }
            }
        if indexer.mappings is not None:
            mappings = conns[es]['mappings']
            mappings[indexer.doc_type] = indexer.mappings

    for es, body in conns.items():
        es.indices.create(index=es._index, body=body)


def delete_index(es):
    return es.indices.delete(index=es._index, ignore=404)


@shared_task
def patch_index(updates):
    """
    Performs a partial update of the ElasticSearch.
    """
    updates_str = ['%s: %d items' % (k, len(v)) for k, v in updates.items()]
    logger.info('Patching index (%s)' % ', '.join(updates_str))

    indexers = _get_registered()
    for doc_type, pks in updates.items():
        for indexer in indexers:
            if indexer.doc_type == doc_type:
                es = get_elasticsearch(indexer)
                bulk(es, indexer.partial_items(pks), raise_on_error=False)


@shared_task
def update_index(remove=True):
    """
    Performs a full update of the ElasticSearch index.
    """
    logger.info('Updating index')

    create_index()

    for indexer in _get_registered():
        # perform full resync
        es = get_elasticsearch(indexer)
        bulk(es, indexer.iterate_items(remove=remove),
             raise_on_error=False,
             request_timeout=30)
