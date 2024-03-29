# -*- coding: utf-8 -*-

from rest_framework import serializers

from tests.models import Author, Book, Unsupported


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ("name", "unique_id")


class BookSerializer(serializers.ModelSerializer):
    tags = serializers.StringRelatedField(many=True)

    class Meta:
        model = Book
        fields = ("id", "tags", "title")


class UnsupportedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unsupported
        field = ("url",)
