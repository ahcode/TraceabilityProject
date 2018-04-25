from django.conf.urls import url
from core import views

urlpatterns = [
	url(r'^$', views.Index.as_view(), name='index'),
	url(r'^new_transaction/$', views.new_transaction),
	url(r'^get_available_inputs/$', views.get_available_inputs),
	url(r'^new_key/$', views.new_key),
	url(r'^test1/$', views.test1),
]