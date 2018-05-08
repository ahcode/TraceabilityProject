# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from core.models import Transaction, T_item

def getDataTree(t_hash):
    t = Transaction.objects.get(t_hash = t_hash)
    pre = {}
    createPreNode(t, pre)
    post = {}
    createPostNode(t, post)
    return (pre, post)

def createPreNode(transaction, dict_item):
    dict_item["stage"] = transaction.transmitter.name
    dict_item["hash"] = transaction.t_hash
    t_inputs = T_item.objects.filter(input_transaction = transaction)
    if t_inputs:
        dict_item["children"] = []
        for i in t_inputs.iterator():
            dict_item["children"].append({})
            createPreNode(i.output_transaction, dict_item["children"][-1])
    else:
        dict_item["origin"] = transaction.origin

def createPostNode(transaction, dict_item):
    dict_item["stage"] = transaction.transmitter.name
    dict_item["hash"] = transaction.t_hash
    t_outputs = T_item.objects.filter(output_transaction = transaction)
    if t_outputs:
        dict_item["children"] = []
        for i in t_outputs.iterator():
            if i.input_transaction:
                dict_item["children"].append({})
                createPostNode(i.input_transaction, dict_item["children"][-1])
        if len(dict_item["children"]) == 0:
            dict_item.pop("children", None)
    else:
        dict_item["destination"] = transaction.destination