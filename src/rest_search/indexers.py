# -*- coding: utf-8 -*-

from django.db.models.signals import post_delete, post_save
from elasticsearch.helpers import scan

from rest_search import get_elasticsearch

_REGISTERED_CLASSES = []


class Indexer(object):
    mappings = None
    private_properties = []

    def __init__(self):
        self.doc_type = self.serializer_class.Meta.model.__name__
        if not hasattr(self, "index"):
            self.index = self.serializer_class.Meta.model.__name__.lower()

    def map_results(self, results):
        """
        Removes ES-specific fields from results.
        """

        def map_result_item(x):
            item = x["_source"]
            for key in self.private_properties:
                item.pop(key, None)
            return item

        return map(map_result_item, results)

    def scan(self, **kwargs):
        es = get_elasticsearch(self)
        return scan(es, index=self.index, doc_type=self.doc_type, **kwargs)

    def search(self, **kwargs):
        es = get_elasticsearch(self)
        return es.search(index=self.index, doc_type=self.doc_type, **kwargs)


def _get_registered():
    """
    Returns instances of all registered indexers.
    """
    return [cls() for cls in _REGISTERED_CLASSES]


def _instance_changed(sender, instance, **kwargs):
    """
    Queues an update to the ElasticSearch index.
    """
    from rest_search import queue_add

    doc_type = instance.__class__.__name__
    queue_add({doc_type: [instance.pk]})


def register(indexer_class):
    """
    Registers an indexer class.
    """
    if indexer_class not in _REGISTERED_CLASSES:
        _REGISTERED_CLASSES.append(indexer_class)

        # register signal handlers
        model = indexer_class.serializer_class.Meta.model
        post_delete.connect(_instance_changed, sender=model)
        post_save.connect(_instance_changed, sender=model)
