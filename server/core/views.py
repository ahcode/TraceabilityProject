# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.views.generic import View, ListView
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from core.models import Public_key, Transaction, T_item, Product
from core.utils import validateTransaction
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA
import json
from datetime import datetime
import time

class Index(View):
	template_name = 'index.html'
	def get(self, request):
		return render(request, self.template_name)

@csrf_exempt
def new_transaction(request):
	if request.method != 'POST':
		return HttpResponse("Solo se permiten peticiones POST")

	try:
		validateTransaction(request.body)
		return HttpResponse("OK")
	except:
		#TODO CAMBIAR ESTO POR UN LOG DE ERRORES
		import traceback
		traceback.print_exc()
		return HttpResponse("ERROR")

@csrf_exempt
def new_key(request):
	if request.method != 'POST':
		return HttpResponse("Solo se permiten peticiones POST")

	try:
		received = json.loads(request.body)
		new_key = Public_key(name = received[0], public_key = received[1])
		new_key.save()
		return HttpResponse("OK")
	except:
		return HttpResponse("ERROR")

@csrf_exempt
def get_available_inputs(request):
	if request.method != 'POST':
		return HttpResponse("Solo se permiten peticiones POST")

	try:
		key_hash = request.POST['pk']
		key = Public_key.objects.get(key_hash = key_hash)
		product = request.POST['product']
		if 'from' in request.POST:
			t_from = request.POST['from']
			ts = Transaction.objects.get(t_hash = t_from)
			o_list = T_item.objects.filter(
				output_transaction__server_timestamp__gt = ts.server_timestamp,
				product__p_id = product,
				receiver = key,
				input_transaction = None
			).order_by('output_transaction__client_timestamp')
		else:
			o_list = T_item.objects.filter(
				product__p_id = product,
				receiver = key,
				input_transaction = None
			).order_by('output_transaction__client_timestamp')
		json_i_list = []

		for o in o_list:
			json_i_list.append((o.output_transaction.t_hash, o.output_index, o.product.p_id, o.quantity))

		return JsonResponse(json_i_list, safe=False)
	except:
		return HttpResponse("ERROR")




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