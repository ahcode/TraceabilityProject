# -*- coding: utf-8 -*-

from os.path import isfile
import sys
import json
import urllib2
from time import time
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA

if len(sys.argv) != 2:
    print("Use: " + sys.argv[0] + " keyname")
    sys.exit()

name = sys.argv[1]

if not isfile("key_" + name + ".pem"):
    print("No existe una clave con ese nombre")
    sys.exit()

key = RSA.importKey(open("key_" + name + ".pem", "r").read())

msg = [
    name,
    key.publickey().exportKey()
]

msg = json.dumps(msg)

req = urllib2.Request('http://127.0.0.1:8000/core/new_key/')
req.add_header('Content-Type', 'application/json')

try:
    response = urllib2.urlopen(req, msg)
    print response.read()
except urllib2.URLError as e:
    print(e.reason)
    
#print pub_key