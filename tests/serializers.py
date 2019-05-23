# -*- coding: utf-8 -*-

from rest_framework import serializers

from tests.models import Book


class BookSerializer(serializers.ModelSerializer):
    tags = serializers.StringRelatedField(many=True)

    class Meta:
        model = Book
        fields = ("id", "tags", "title")
