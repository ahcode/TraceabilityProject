# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls import url
from core import api

urlpatterns = [
	url(r'^new_transaction/$', api.new_transaction),
	url(r'^get_available_inputs/$', api.get_available_inputs),
	url(r'^new_key/$', api.new_key),
]