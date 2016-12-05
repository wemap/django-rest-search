# -*- coding: utf-8 -*-

import logging

from celery import shared_task
from elasticsearch.helpers import bulk

from rest_search import get_elasticsearch
from rest_search.indexers import _get_registered


logger = logging.getLogger('rest_search')


@shared_task
def patch_index(updates):
    """
    Performs a partial update of the ElasticSearch.
    """
    updates_str = ['%s: %d items' % (k, len(v)) for k, v in updates.items()]
    logger.info('Patching index (%s)' % ', '.join(updates_str))

    es = get_elasticsearch()
    indexers = _get_registered()
    for doc_type, pks in updates.items():
        for indexer in indexers:
            if indexer.doc_type == doc_type:
                bulk(es, indexer.partial_items(pks), raise_on_error=False)


@shared_task
def update_index():
    """
    Performs a full update of the ElasticSearch index.
    """
    logger.info('Updating index')

    es = get_elasticsearch()
    indexers = _get_registered()

    # create indices
    indices = {}
    for indexer in indexers:
        if indexer.index not in indices:
            indices[indexer.index] = {
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
                },
            }
        if indexer.mappings is not None:
            mappings = indices[indexer.index]['mappings']
            mappings[indexer.doc_type] = indexer.mappings

    for index, body in indices.items():
        es.indices.create(index=index, body=body, ignore=400)

    # perform full index resync
    for indexer in indexers:
        bulk(es, indexer.iterate_items(es),
             raise_on_error=False,
             request_timeout=30)
