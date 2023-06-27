# -*- coding: utf-8 -*-

from rest_framework import serializers

from tests.models import Author, Book


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ("id", "name")


class BookSerializer(serializers.ModelSerializer):
    tags = serializers.StringRelatedField(many=True)

    class Meta:
        model = Book
        fields = ("id", "tags", "title")
