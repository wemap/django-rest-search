# -*- coding: utf-8 -*-

import uuid

from django.db import models
from django.db.models.signals import post_delete, post_save
from elasticsearch.helpers import scan

from rest_search import get_elasticsearch

_REGISTERED_CLASSES = []


class Indexer(object):
    mappings = None
    private_properties = []

    def __init__(self):
        model = self.serializer_class.Meta.model
        self.doc_type = model.__name__
        if not hasattr(self, "index"):
            self.index = model.__name__.lower()

        # Find the model's primary key.
        primary_key = model._meta.pk

        # Make a note of the field name.
        self.pk_name = primary_key.name

        # Determine how an `_id` from ElasticSearch is parsed to
        # a primary key value.
        if isinstance(primary_key, models.UUIDField):
            self.pk_from_string = uuid.UUID
        elif isinstance(primary_key, (models.AutoField, models.BigAutoField)):
            self.pk_from_string = int
        else:
            raise AssertionError("Unhandled primary key type %s" % type(primary_key))

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
        return scan(es, index=self.index, **kwargs)

    def search(self, **kwargs):
        es = get_elasticsearch(self)
        return es.search(index=self.index, **kwargs)


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
