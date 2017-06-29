# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models


class Source(models.Model):
    name = models.CharField(max_length=100)
    web_url = models.CharField(max_length=150, null=True)
    screen_name = models.CharField(max_length=50)


class SourceParameters(models.Model):
    source = models.ForeignKey(Source)
    seconds_to_monitor = models.IntegerField(default=60*5)
    tweets_to_get = models.IntegerField(default=15)
    score_threshold = models.FloatField(default=0.6)
    terms_per_article = models.IntegerField(default=5)
    version = models.IntegerField(null=True)


class Article(models.Model):
    source = models.ForeignKey(Source)
    news_url = models.CharField(max_length=200, null=True)
    file_path = models.CharField(max_length=200, null=True)
    extracted = models.IntegerField(default=0, null=True)

class Term(models.Model):
    article = models.ForeignKey(Article)
    text = models.CharField(max_length=100)
    score = models.FloatField()


class Tweet(models.Model):
    source = models.ForeignKey(Source)
    article = models.ForeignKey(Article)
    created_at = models.DateTimeField()


class Stat(models.Model):
    tweet = models.ForeignKey(Tweet)
    likes_count = models.IntegerField()
    shares_count = models.IntegerField()
    checked_at = models.DateTimeField(auto_now_add=True)


class TrendFactor(models.Model):
    source = models.ForeignKey(Source)
    exposition = models.FloatField()
    activity = models.FloatField()
    time_delay = models.FloatField()
    tfidf_weight = models.FloatField()
