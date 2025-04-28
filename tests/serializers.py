# -*- coding: utf-8 -*-

from rest_framework import serializers

from tests.models import Author, Book, Tag, Unsupported


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ("name", "unique_id")


class BookSerializer(serializers.ModelSerializer):
    tags = serializers.SlugRelatedField(
        many=True, queryset=Tag.objects.all(), slug_field="slug"
    )

    class Meta:
        model = Book
        fields = ("id", "tags", "title")


class UnsupportedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Unsupported
        field = ("url",)
