# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from models import Transaction, T_item, Public_key, Product
from Crypto.Hash import SHA256
from Crypto.Signature import PKCS1_v1_5
from Crypto.PublicKey import RSA
from datetime import datetime
import json

def validateTransaction(raw_transaction):
    #Decodificando json transacción
    try: transaction = json.loads(raw_transaction)
    except: raise Exception("Transaction json codification error.")
    
    #Comprobando número de elementos de transacción
    if len(transaction) != 2:
        raise Exception("Incorrect transaction format.")

    raw_data = transaction[0]
    sign = transaction[1]

    #Decodificando json datos
    try: data = json.loads(raw_data)
    except: raise Exception("Data json codification error.")

    #Comprobando número de elementos de datos
    if len(data) == 4:
        additional = {}
    elif len(data) == 5:
        additional = data[4]
    else:
        raise Exception("Incorrect data format.")
    
    try: timestamp = datetime.fromtimestamp(data[0])
    except: raise Exception("Timestamp format error.")
    #TODO SOLUCINAR WARNING AL FORMATEAR TIMESTAMP
    
    pk_hash = data[1]
    inputs = data[2]
    outputs = data[3]
    
    #Comprobando clave emisor
    try: pk = Public_key.objects.get(key_hash = pk_hash, active = True)
    except Public_key.DoesNotExist: raise Exception("Public Key does not exist or is unactive.")

    #Comprobando firma
    data_hash = SHA256.new(raw_data)
    validateSign(data_hash, sign, pk.public_key)

    #Generando transacción
    new_transaction = Transaction(
		t_hash = data_hash.hexdigest(),
		client_timestamp = datetime.fromtimestamp(data[0]),
		transmitter = pk,
		sign = sign,
		data_string = raw_data
	)

    #Añadiendo información adicional a la transacción
    if 'origin' in additional: new_transaction.origin = additional['origin']
    if 'destination' in additional: new_transaction.destination = additional['destination']
    if 'batchid' in additional: new_transaction.batch_id = additional['batchid']
    if 'operator' in additional: new_transaction.operator = additional['operator']

    (db_inputs, db_outputs) = validateInputsOutputs(inputs, outputs, additional, pk)

    saveItems(new_transaction, db_inputs, db_outputs)

def validateSign(data_hash, sign, pk):
    #Comprueba que la firma de una transacción sea correcta
    keyobject = RSA.importKey(pk)
    verifier = PKCS1_v1_5.new(keyobject)

    if verifier.verify(data_hash, sign.decode('hex')) == False:
        raise Exception("Sign is not correct!")

def validateInputsOutputs(inputs, outputs, additional, pk):
    try:
        #Comprobar tipo de dato inputs
        assert isinstance(inputs, list)
        inputs_dbobjects_list = []
        inputs_total_quantity = 0

        #Comprobar inputs
        for i in range(0, len(inputs)):
            assert isinstance(inputs[i], list)
            assert len(inputs[i]) == 2
            try: item = T_item.objects.get(output_transaction__t_hash = inputs[i][0], output_index = inputs[i][1], receiver = pk, input_transaction = None)
            except T_item.DoesNotExist: Exception("An input item is not valid.")
            item.input_index = i
            inputs_total_quantity += item.quantity
            inputs_dbobjects_list.append(item)
    
    except AssertionError:
        raise Exception("Inputs format is not correct.")

    #Comprobar si el tipo de producto de entrada es igual
    if len(inputs_dbobjects_list) != 0:
        equal_inputs = all(inputs_dbobjects_list[0].product == item.product for item in inputs_dbobjects_list)
    
    try:
        assert isinstance(outputs, list)
        outputs_dbobjects_list = []
        outputs_total_quantity = 0

        #Generar outputs
        for i in range(0, len(outputs)):
            assert isinstance(outputs[i], list)
            assert len(outputs[i]) == 3
            quantity = outputs[i][2]
            assert isinstance(quantity, int)
            assert quantity > 0
            try: pk_receiver = Public_key.objects.get(key_hash = outputs[i][0], active = True)
            except Public_key.DoesNotExist: raise Exception("An output receiver is not valid.")
            try: product_type = Product.objects.get(p_id = outputs[i][1])
            except Product.DoesNotExist: raise Exception("An output product is not valid.")
            item = T_item(
                output_index = i,
                receiver = pk_receiver,
                product = product_type,
                quantity = quantity
            )
            outputs_total_quantity += quantity
            outputs_dbobjects_list.append(item)
    
    except AssertionError:
        raise Exception("Outputs format is not correct.")
    
    #Comprobar mismo tipo de producto en inputs y outputs
    if len(outputs_dbobjects_list) != 0 and len(inputs_dbobjects_list) != 0:
        same_type = all(inputs_dbobjects_list[0].product == item.product for item in inputs_dbobjects_list + outputs_dbobjects_list)
    
    #Transacción sin inputs ni outputs
    if len(inputs_dbobjects_list) == 0 and len(outputs_dbobjects_list) == 0:
        raise Exception("Transactions without inputs or outputs are forbidden.")
    #Transacción generadora
    elif len(inputs_dbobjects_list) == 0 and len(outputs_dbobjects_list) == 1:
        if outputs_dbobjects_list[0].receiver != pk:
            raise Exception("Generating transactions receiver have to be the transaction transmitter")
        if 'origin' not in additional:
            raise Exception("Generating transactions have to specify origin.")
        if 'destination' in additional:
            raise Exception("Generating transactions can't specify destination.")
    #Transacción destructora
    elif len(outputs_dbobjects_list) == 0 or (len(inputs_dbobjects_list) == 1 and len(outputs_dbobjects_list) == 1 and same_type and outputs_total_quantity < inputs_total_quantity):
        if len(inputs_dbobjects_list) != 1:
            raise Exception("Destructive transactions must have only one input")
        if len(outputs_dbobjects_list) == 1 and outputs_dbobjects_list[0].receiver != pk:
            raise Exception("Destructive transactions receiver have to be the transaction transmitter")
        if 'origin' in additional:
            raise Exception("Destructive transactions can't specify origin.")
        if 'destination' not in additional:
            raise Exception("Destructive transactions have to specify destination.")
    #Transacción con el mismo tipo de producto
    elif same_type:
        if outputs_total_quantity != inputs_total_quantity:
            raise Exception("In same product transactions, inputs and outputs quantity must be equal")
    #En transacciones con distinto tipo de producto no se realizan comprobaciones

    return (inputs_dbobjects_list, outputs_dbobjects_list)

def saveItems(transaction, inputs, outputs):
    #Guardar transacción
    try: transaction.save()
    except: raise Exception("Error saving transaction")
    
    #Actualizar inputs
    for i in range(0, len(inputs)):
        inputs[i].input_transaction = transaction
        try: inputs[i].save()
        except:
            #Revertir cambios
            for j in range(0, i):
                inputs[i].input_transaction = None
                inputs[i].input_index = None
                inputs[i].save()
            transaction.delete()
            raise Exception("Error updating an input item")
    
    #Guardar outputs
    for i in range(0, len(outputs)):
        outputs[i].output_transaction = transaction
        try: outputs[i].save()
        except:
            #Revertir cambios
            for j in range(0, i):
                outputs[i].delete()
            for j in range(0, len(inputs)):
                inputs[i].input_transaction = None
                inputs[i].input_index = None
                inputs[i].save()
            transaction.delete()
            raise Exception("Error saving an output item")