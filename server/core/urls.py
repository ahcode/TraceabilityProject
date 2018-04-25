from django.conf.urls import url
from core import api

urlpatterns = [
	url(r'^$', api.Index.as_view(), name='index'),
	url(r'^new_transaction/$', api.new_transaction),
	url(r'^get_available_inputs/$', api.get_available_inputs),
	url(r'^new_key/$', api.new_key),
	url(r'^test1/$', api.test1),
]