# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-29 02:07
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('trend', '0003_auto_20170629_0125'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='url',
        ),
    ]
