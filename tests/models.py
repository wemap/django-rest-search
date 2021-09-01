# -*- coding: utf-8 -*-

from django.db import models


class Book(models.Model):
    title = models.CharField(max_length=200)
    tags = models.ManyToManyField("Tag")


class Tag(models.Model):
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.slug
