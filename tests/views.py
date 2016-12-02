# -*- coding: utf-8 -*-

from rest_framework.generics import CreateAPIView

from tests.serializers import BookSerializer


class BookCreate(CreateAPIView):
    serializer_class = BookSerializer
