INSTALLED_APPS = [
    'rest_framework',
    'rest_search',
    'tests',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
    }
}

REST_SEARCH = {
    'HOST': 'es.example.com',
}

SECRET_KEY = '_%2pegfm%-&32ekj_+aqr468-*8lkt7zbeyl)*0#f-@56#$k_)'
