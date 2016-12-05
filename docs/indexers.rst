Indexers
========

Indexers provide the binding between the data in the ORM and the data which
is indexed in ElasticSearch.

To perform data serialization, indexers build upon the REST framework's
serializers, which allow great flexibility in how you map the data in the ORM
and the JSON representation which is sent to ElasticSearch.

Declaring indexers
------------------

For example, let's consider the following model::

    class Book(models.Model):
        title = models.CharField(max_length=200)

You would start with a simple serializer::

    class BookSerializer(serializers.ModelSerializer):
        class Meta:
            model = Book
            fields = (
                'id',
                'title',
            )

You can then create an indexer::

    from rest_search import indexers

    class BookIndexer(indexers.Indexer):
        index = 'some_index'
        serializer_class = BookSerializer

        def get_queryset(self):
            return Book.objects.all()

And finally you register the indexer::

    indexers.register(BookIndexer)

Index updates
-------------

When you register an indexer, it will install signal handlers for save and
delete events and queue updates to the ElasticSearch index.

For these updates to actually be performed, either install the
```rest_search.middleware.FlushUpdatesMiddleware``` middleware or wrap your
code using the ```rest_search.decorators.flush_updates``` decorator.
