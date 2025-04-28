# -*- coding: utf-8 -*-

from django.urls import path
from rest_framework.routers import SimpleRouter

from tests import views

router = SimpleRouter(trailing_slash=False)
router.register("authors", views.AuthorViewSet, basename="author")
router.register("books", views.BookViewSet, basename="book")

urlpatterns = [
    path("books/search", views.BookSearch.as_view()),
    path("books/search_sorted", views.BookSearchSorted.as_view()),
] + router.urls
