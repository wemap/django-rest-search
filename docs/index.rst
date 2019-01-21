Django REST Search
==================

Django REST Search provides a set of classes to facilitate the integration of
ElasticSearch [1]_ into applications powered by the Django REST Framework [2]_.

Installation
------------

The easiest way to install Django REST Search is using pip.

.. code-block:: shell

    pip install djangorestsearch

Add `'rest_search'` to your `INSTALLED_APPS` setting.

.. code-block:: python

    INSTALLED_APPS = [
        ...
        'rest_search',
    ]

Add the middleware to flush ElasticSearch updates to a celery task.

.. code-block:: python

    MIDDLEWARE = [
        ...
        'rest_search.middleware.FlushUpdatesMiddleware',
    ]

Configure your ElasticSearch connection.

.. code-block:: python

    REST_SEARCH_CONNECTIONS = {
        'default': {
            'HOST': 'es.example.com',
        }
    }

If you wish, you can customise the settings used when creating an index.

.. code-block:: python

   REST_SEARCH_INDEX_SETTINGS = {
       'analysis': {
           'analyzer': {
               'default': {
                   'tokenizer': 'standard',
                   'filter': [
                       'standard',
                       'lowercase',
                       'asciifolding',
                   ]
               }
           }
       }
   }

Contents
--------

.. toctree::
   :maxdepth: 2

   indexers
   tasks

.. [1] https://www.elastic.co/products/elasticsearch

.. [2] http://www.django-rest-framework.org/
