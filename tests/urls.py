# -*- coding: utf-8 -*-

from django.conf.urls import url

from tests import views

urlpatterns = [
    url(r'^books$', views.BookCreate.as_view()),
    url(r'^books/search$', views.BookSearch.as_view()),
]
