# -*- coding: utf-8 -*-

import logging

from celery import shared_task
from elasticsearch.helpers import bulk

from rest_search import get_elasticsearch, get_indexers


logger = logging.getLogger('rest_search')


@shared_task
def index_data():
    logger.info('Rebuilding index')

    es = get_elasticsearch()
    indexers = get_indexers()

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


@shared_task
def index_partial(queues):
    updates = ['%s: %d' % (k, len(v)) for k, v in queues.items()]
    logger.info('Updating index (%s)' % ', '.join(updates))

    es = get_elasticsearch()
    indexers = get_indexers()
    for doc_type, pks in queues.items():
        for indexer in indexers:
            if indexer.doc_type == doc_type:
                bulk(es, indexer.partial_items(pks), raise_on_error=False)
