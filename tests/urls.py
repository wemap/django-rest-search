# -*- coding: utf-8 -*-

from django.urls import path

from tests import views

urlpatterns = [
    path("books", views.BookCreate.as_view()),
    path("books/search", views.BookSearch.as_view()),
    path("books/search_sorted", views.BookSearchSorted.as_view()),
]
