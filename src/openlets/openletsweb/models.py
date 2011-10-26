from django.db import models as m
from django.contrib.auth.models import User

class Person(m.Model):
	user = m.ForeignKey(User)
	default_currency = m.ForeignKey('Currency')
	balances = m.ManyToManyField('Balance')


class Balance(m.Model):
	"""A balance between two people.
	"""
	currency = m.ForeignKey('Currency')
	value = m.IntegerField(default=0)


class Transaction(m.Model):
	""" """
	provider_record = m.ForeignKey('TransactionRecord')
	receiver_record = m.ForeignKey('TransactionRecord')
	time_confirmed = m.DateTimeField(auto_now_add=True)


class TransactionRecord(m.Model):
	""" """
	provider = m.ForeignKey('Person')
	receiver = m.ForeignKey('Person')
	currency = m.ForeignKey('Currency')
	from_provider = m.BooleanField()
	time_created = m.DateTimeField(auto_now_add=True)


class Currency(m.Model):
	""" """
	name = m.CharField(max_length=255)
	description = m.TextField()
	decimal_places = m.IntegerField(default=0)
	creator = m.ForeignKey(Person)
	default = m.BooleanField(default=False)
	time_created = m.DateTimeField(auto_now_add=True)
