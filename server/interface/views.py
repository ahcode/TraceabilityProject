# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import TemplateView
from django.http import HttpResponse
from core.models import T_item

class Index(TemplateView):
	template_name = 'index.html'

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