# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from trend.models import Source, SourceParameters, TrendFactor

admin.site.register(TrendFactor)
admin.site.register(Source)
admin.site.register(SourceParameters)
# Register your models here.
