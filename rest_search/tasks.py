# -*- coding: utf-8 -*-

import logging

from celery import shared_task
from django.conf import settings
from elasticsearch.helpers import bulk

from rest_search import DEFAULT_INDEX_SETTINGS, get_elasticsearch
from rest_search.indexers import _get_registered

logger = logging.getLogger("rest_search")


def create_index():
    """
    Creates the ElasticSearch indices if they do not exist.
    """
    for indexer in _get_registered():
        _create_index(indexer)


def delete_index():
    """
    Deletes the ElasticSearch indices.
    """
    for indexer in _get_registered():
        es = get_elasticsearch(indexer)
        es.indices.delete(index=indexer.index, ignore=404)


@shared_task
def patch_index(updates):
    """
    Performs a partial update of the ElasticSearch indices.
    """
    updates_str = ["%s: %d items" % (k, len(v)) for k, v in updates.items()]
    logger.info("Patching indices (%s)" % ", ".join(updates_str))

    indexers = _get_registered()
    for doc_type, pks in updates.items():
        for indexer in indexers:
            if indexer.doc_type == doc_type:
                _patch_index(indexer, pks)


@shared_task
def update_index(remove=True):
    """
    Performs a full update of the ElasticSearch indices.
    """
    logger.info("Updating indices")

    create_index()

    for indexer in _get_registered():
        _update_index(indexer, remove=remove)


def _create_index(indexer):
    body = {
        "mappings": {},
        "settings": getattr(
            settings, "REST_SEARCH_INDEX_SETTINGS", DEFAULT_INDEX_SETTINGS
        ),
    }
    if indexer.mappings is not None:
        body["mappings"][indexer.doc_type] = indexer.mappings

    es = get_elasticsearch(indexer)
    if not es.indices.exists(indexer.index):
        logger.info("Creating index %s" % indexer.index)
        es.indices.create(index=indexer.index, body=body)


def _delete_items(indexer, pks):
    es = get_elasticsearch(indexer)

    def mapper(pk):
        return {
            "_index": indexer.index,
            "_type": indexer.doc_type,
            "_id": pk,
            "_op_type": "delete",
        }

    bulk(es, map(mapper, pks), raise_on_error=False)


def _index_items(indexer, pks):
    es = get_elasticsearch(indexer)
    seen_pks = set()

    def bulk_mapper(block_size=1000):
        for i in range(0, len(pks), block_size):
            chunk = pks[i : i + block_size]
            qs = indexer.get_queryset().filter(pk__in=chunk)
            data = indexer.serializer_class(qs, many=True).data
            for item in data:
                seen_pks.add(item["id"])
                yield {
                    "_index": indexer.index,
                    "_type": indexer.doc_type,
                    "_id": item["id"],
                    "_source": item,
                }

    bulk(es, bulk_mapper())
    return seen_pks


def _patch_index(indexer, pks):
    # index current items
    seen_pks = _index_items(indexer, pks)

    # remove obsolete items
    removed_pks = set(pks) - seen_pks
    _delete_items(indexer, removed_pks)


def _update_index(indexer, remove):
    scan = indexer.scan(query={"stored_fields": []})
    old_pks = set([int(i["_id"]) for i in scan])

    # index current items
    seen_pks = _index_items(
        indexer, sorted(indexer.get_queryset().values_list("pk", flat=True))
    )

    # remove obsolete items
    if remove:
        removed_pks = old_pks - seen_pks
        _delete_items(indexer, removed_pks)
