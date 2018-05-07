# -*- coding: utf-8 -*-

import json
import urllib
import urllib2
from time import time
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5

new_transaction_dir = "new_transaction/"
get_inputs_dir = "get_available_inputs/"

class Connection:
    def __init__(self, api_url, pem_file, mode):
        if not isinstance(api_url, basestring): raise Exception("api_url must be a string")
        self.api_url = api_url
        self.__apicheck()

        if not isinstance(pem_file, basestring): raise Exception("pem_file must be a string")
        self.key = RSA.importKey(open(pem_file, "r").read())
        if not self.key.has_private(): raise Exception("key doesn't have private part")

        if mode == 'merge': self.mode = 1
        elif mode == 'serial': self.mode = 2
        elif mode == 'arbitrary': self.mode = 3
        else: raise Exception("mode must be 'merge', 'serial' or 'arbitrary'")
        
        self.inputs_queue = {} #(Transaction, nº output, product, quantity)
        self.last_transaction_received = {}

    def __apicheck(self):
        return True
        #POR DEFINIR
        #Conectar a la api y esperar una determinada respuesta
        #Si no se recibe lanzar excepción

    def __getinputslist(self, product):
        if str(product) not in self.inputs_queue:
            self.inputs_queue[str(product)] = []
        
        values = {
            'pk' : self.getkeyhash(),
            'product' : product
        }

        if str(product) in self.last_transaction_received:
            values['from'] = self.last_transaction_received[str(product)]
        
        data = urllib.urlencode(values)
        req = urllib2.Request(self.api_url + get_inputs_dir, data)
        response = urllib2.urlopen(req).read()
        #HACER ALGO CUANDO EL SERVIDOR NO RESPONDA
        if response == "ERROR":
            raise Exception("Error getting available inputs")
        response = json.loads(response)

        self.inputs_queue[str(product)].extend(response)
        self.last_transaction_received[str(product)] = self.inputs_queue[str(product)][-1][0]
        # FALTA no está claro el orden de la lista ¿server_timestamp o client_timestamp?

    def __merge(self, product):
        if len(self.inputs_queue[str(product)]) > 1:
            inputs = []
            quantity = 0
            for i in self.inputs_queue[str(product)]:
                inputs.append((i[0], i[1]))
                quantity += i[3]
            if inputs:
                outputs = [(self.getkeyhash(), product, quantity)]
                t_hash = self.__newtransaction(inputs, outputs)
                self.inputs_queue[str(product)] = [(t_hash, 0, product, quantity)] 

    def getkeyhash(self):
        return SHA256.new(self.key.publickey().exportKey()).hexdigest()

    def __gettransactionhash(self, data):
        return SHA256.new(data).hexdigest()

    def __sign(self, data):
        data_hash = SHA256.new(data)
        signer = PKCS1_v1_5.new(self.key)
        return signer.sign(data_hash).encode('hex')

    def __newtransaction(self, inputs, outputs, additional = {}):
        data = [ time(), self.getkeyhash(), inputs, outputs ]
        if additional:
            data.append(additional)

        data = json.dumps(data)

        firma = self.__sign(data)
        
        transaction = [ data, firma ]
        transaction = json.dumps(transaction)

        req = urllib2.Request(self.api_url + new_transaction_dir)
        req.add_header('Content-Type', 'application/json')
        try: response = urllib2.urlopen(req, transaction)
        #TODO Sustituir excepción por un buffer de transacciones hasta que el
        #servidor vuelva a estar disponible
        except: raise Exception("Error connecting to server")

        #La respuesta nunca debería ser errónea ya que la clase Connection se encarga
        #de que todas las transacciones enviadas sean válidas
        if response.read() == "ERROR":
            raise Exception("Error sending a transaction")

        return self.__gettransactionhash(data)

    def __getinput(self, product, batch_id = None):
        #AÑADIR control de errores (si no hay outputs disponibles)
        self.__getinputslist(product)

        if self.mode == 1:
            self.__merge(product)
            return self.inputs_queue[str(product)].pop(0)
        elif self.mode == 2:
            return self.inputs_queue[str(product)].pop(0)
        elif self.mode == 3:
            if not batch_id:
                raise Exception("Arbitrary mode must specific 'batch_id'")
            #FALTA buscar ese batch id en inputs_queue y devolverlo

    def generate(self, product, quantity, *args, **kwargs):
        if 'origin' not in kwargs:
            raise Exception("Origin is needed in generating transactions.")
        outputs = [(self.getkeyhash(), product, quantity)]
        return self.__newtransaction([], outputs, kwargs)

    def destroy(self, product, quantity, *args, **kwargs):
        if 'destination' not in kwargs:
            raise Exception("Destination is needed in destructive transactions.")
        if 'batch_id' in kwargs: bid = kwargs['batch_id']
        else: bid = None
        input_data = self.__getinput(product, bid)
        inputs = [(input_data[0], input_data[1])]
        outputs = []
        left = input_data[3] - quantity

        if left > 0:
            outputs.append((self.getkeyhash(), product, left))
        elif left < 0:
            raise Exception("Error with transaction quantity")

        t_hash = self.__newtransaction(inputs, outputs, kwargs)
        if left > 0:
            self.inputs_queue[str(product)].insert(0, (t_hash, 1, product, left))

    def send(self, receiver, product, quantity, *args, **kwargs):
        if 'batch_id' in kwargs: bid = kwargs['batch_id']
        else: bid = None
        input_data = self.__getinput(product, bid)
        inputs = [(input_data[0], input_data[1])]
        outputs = [(receiver, product, quantity)]
        left = input_data[3] - quantity

        if left > 0:
            outputs.append((self.getkeyhash(), product, left))
        elif left < 0:
            raise Exception("Error with transaction quantity")

        t_hash = self.__newtransaction(inputs, outputs, kwargs)
        if left > 0:
            self.inputs_queue[str(product)].insert(0, (t_hash, 1, product, left))

    def send_all(self, receiver, product, *args, **kwargs):
        self.__getinputslist(product)
        total = 0
        for i in self.inputs_queue[product]:
            total += i[2]
        self.send(receiver, product, total, *args, **kwargs)
    
    def change_type(self, product_in, quantity_in, product_out, quantity_out, *args, **kwargs):
        if 'batch_id' in kwargs: bid = kwargs['batch_id']
        else: bid = None
        input_data = self.__getinput(product_in, bid)
        inputs = [(input_data[0], input_data[1])]
        outputs = [(self.getkeyhash(), product_out, quantity_out)]
        left = input_data[3] - quantity_in

        if left > 0:
            outputs.append((self.getkeyhash(), product_in, left))
        elif left < 0:
            raise Exception("Error with transaction quantity")

        t_hash = self.__newtransaction(inputs, outputs, kwargs)
        if left > 0:
            self.inputs_queue[str(product_in)].insert(0, (t_hash, 1, product_in, left))
        return