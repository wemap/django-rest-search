# -*- coding: utf-8 -*-

import uuid

from django.db import models


class Author(models.Model):
    """
    This model's primary key is a `UUIDField`.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=200)


class Book(models.Model):
    title = models.CharField(max_length=200)
    tags = models.ManyToManyField("Tag")


class Tag(models.Model):
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.slug
