INSTALLED_APPS = [
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'rest_framework',
    'rest_search',
    'tests',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    }
}

MIDDLEWARE_CLASSES = [
    'django.middleware.common.CommonMiddleware',
    'rest_search.middleware.FlushUpdatesMiddleware',
]

REST_SEARCH_CONNECTIONS = {
    'default': {
        'HOST': 'es.example.com',
        'INDEX_NAME': 'bogus',
    }
}

ROOT_URLCONF = 'tests.urls'

SECRET_KEY = '_%2pegfm%-&32ekj_+aqr468-*8lkt7zbeyl)*0#f-@56#$k_)'
