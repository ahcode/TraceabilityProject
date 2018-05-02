# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.conf.urls import url
from interface import views

urlpatterns = [
	url(r'^$', views.Index.as_view(), name='index'),
	url(r'^graph/(?P<tid>[a-z0-9]+)/$', views.TransactionsGraph.as_view(), name='tgraph'),
	url(r'^transactions/$', views.TransactionList.as_view(), name='tlist'),
	url(r'^transactions/(?P<slug>[a-z0-9]+)/$', views.TransactionDetail.as_view(), name='tdetails'),
	url(r'^test1/$', views.test1),
]