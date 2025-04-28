Celery Tasks
============

Django REST Search relies on the Celery [1]_ distributed task queue to
perform updates to the OpenSearch index.

There are two tasks:

- ```rest_search.tasks.update_index``` performs a full update of the
  OpenSearch index by iterating over all the items for which an
  indexer has been defined. You will need to perform this at least once
  when you start using Django REST Search or whenever you add an indexer.

- ```rest_search.tasks.patch_index``` performs a partial update of the
  OpenSearch index for specific items. You usually do not need to invoke
  this yourself, as the indexer sets the required signal handlers when it is
  registered.

.. [1] http://www.celeryproject.org/
