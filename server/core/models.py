# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from datetime import datetime
from django.core.validators import MinValueValidator
from Crypto.Hash import SHA256

# Create your models here.
class Public_key(models.Model):
    key_hash = models.CharField(max_length = 64, unique = True, blank = True, primary_key = True)
    name = models.CharField(max_length = 50, unique = True)
    public_key = models.TextField(max_length = 300)
    description = models.TextField(max_length = 300, blank = True)
    active = models.BooleanField(default = False)
    def save(self, *args, **kwargs):
        self.key_hash = SHA256.new(self.public_key).hexdigest()
        super(Public_key, self).save(*args, **kwargs)
    def __str__(self):
        return self.name

class Product(models.Model):
    p_id = models.CharField(max_length = 50, primary_key = True)
    name = models.CharField(max_length = 50, unique = True)
    measure_unit = models.CharField(max_length = 50)
    description = models.TextField(max_length = 300, blank = True)
    def __str__(self):
        return str(self.p_id) + ". " + self.name

class Transaction(models.Model):
    t_hash = models.CharField(max_length = 64, primary_key = True)
    server_timestamp = models.DateTimeField(auto_now=True)
    client_timestamp = models.DateTimeField()
    transmitter = models.ForeignKey(Public_key, on_delete=models.CASCADE)
    batch_id = models.CharField(max_length = 64, null = True)
    origin = models.CharField(max_length = 64, null = True)
    destination = models.CharField(max_length = 64, null = True)
    operator = models.CharField(max_length = 64, null = True)
    sign = models.CharField(max_length = 256)
    data_string = models.CharField(max_length=1000)
    def __str__(self):
        return self.t_hash

class T_item(models.Model):
    class Meta:
        unique_together = (('output_transaction', 'output_index'),)
    output_transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='output')
    output_index = models.IntegerField()
    receiver = models.ForeignKey(Public_key, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(validators = [MinValueValidator(0)])
    input_transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, blank=True, null=True, related_name='input')
    input_index = models.IntegerField(blank = True, null = True)
    def __str__(self):
        return self.output_transaction.__str__() + " - " + str(self.output_index)