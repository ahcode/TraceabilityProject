# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import TemplateView, ListView, DetailView
from django.http import HttpResponse
from core.models import Transaction, T_item
from utils import getDataTree
import json

class Index(TemplateView):
	template_name = 'index.html'

class TransactionList(ListView):
	model = Transaction
	template_name = 'transactionList.html'
	queryset = Transaction.objects.all().order_by('-client_timestamp')
	context_object_name = 'transaction_list'

class TransactionDetail(DetailView):
	model = Transaction
	template_name = 'transactionDetail.html'
	context_object_name = 't'
	slug_field = 't_hash'

	def get_context_data(self, **kwargs):
		context = super(TransactionDetail, self).get_context_data(**kwargs)
		context['inputs'] = T_item.objects.filter(input_transaction = context['t']).order_by('input_index')
		context['outputs'] = T_item.objects.filter(output_transaction = context['t']).order_by('output_index')
		return context

class TransactionsGraph(TemplateView):
	template_name = 'graph.html'

	def get_context_data(self, **kwargs):
		context = super(TransactionsGraph, self).get_context_data(**kwargs)
		(pre, post) = getDataTree(self.kwargs["tid"])
		context["dataTreePre"] = json.dumps(pre)
		context["dataTreePost"] = json.dumps(post)
		return context

#ESTO ES SOLO UNA PRUEBA
def test1(request):
	return HttpResponse(getQuantityProductsPerKey())
def getQuantityProductsPerKey():
	outputs = T_item.objects.filter(input_transaction = None)
	dic = {}
	for o in outputs:
		if o.receiver.name not in dic:
			dic[o.receiver.name] = {}
		if o.product.name not in dic[o.receiver.name]:
			dic[o.receiver.name][o.product.name] = 0
		dic[o.receiver.name][o.product.name] += o.quantity
	text = ""
	for key, pdic in dic.iteritems():
		text = text + "---" + key + "---</br>"
		for product, quantity in pdic.iteritems():
			text = text + product + " = " + str(quantity) + "</br>"
	return text