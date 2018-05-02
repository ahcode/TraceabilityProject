# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from core.models import Transaction, T_item

def getDataTree(t_hash):
    t = Transaction.objects.get(t_hash = t_hash)
    dataTree = {}
    createNode(t, dataTree)
    return dataTree

def createNode(transaction, dict_item):
    dict_item["stage"] = transaction.transmitter.name
    dict_item["hash"] = transaction.t_hash
    t_inputs = T_item.objects.filter(input_transaction = transaction)
    if t_inputs:
        dict_item["children"] = []
        for i in t_inputs.iterator():
            dict_item["children"].append({})
            createNode(i.output_transaction, dict_item["children"][-1])
    else:
        dict_item["origin"] = transaction.origin