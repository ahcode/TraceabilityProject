# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from core import models

# Register your models here.
admin.site.register(models.Public_key)
admin.site.register(models.Product)
admin.site.register(models.Transaction)
admin.site.register(models.T_item)
