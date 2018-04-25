# -*- coding: utf-8 -*-

from Crypto.PublicKey import RSA
from os.path import isfile
import sys

if len(sys.argv) != 2:
    print("Use: " + sys.argv[0] + " keyname")
    sys.exit()

name = sys.argv[1]

if isfile("key_" + name + ".pem"):
    inp = raw_input("Ya existe una clave con ese nombre ¿Desea sobreescribirla? (S/N): ")
    if inp != "S" and inp !="s":
        sys.exit()

private_key = RSA.generate(1024)
public_key = private_key.publickey()

key_f = open("key_" + name + ".pem", "w")

key_f.write(private_key.exportKey())

key_f.close()