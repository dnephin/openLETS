from django.db import models as m
from django.contrib.auth.models import User


currency_field = lambda: m.ForeignKey('Currency', related_name='+')


class Person(m.Model):
	""" """
	user = m.ForeignKey(User)
	default_currency = currency_field()
	balances = m.ManyToManyField('Balance', related_name='persons')


class Balance(m.Model):
	"""A balance between two people.
	"""
	credited_person = m.ForeignKey('Person')
	currency = currency_field()
	value = m.IntegerField(default=0)


class Transaction(m.Model):
	""" """

	class Meta:
		unique_together = ('provider_record', 'receiver_record')

	provider_record = m.OneToOneField(
		'TransactionRecord', 
		related_name='provider_transaction'
	)
	receiver_record = m.OneToOneField(
		'TransactionRecord', 
		related_name='receiver_transaction'
	)
	resolved = m.BooleanField()
	time_confirmed = m.DateTimeField(auto_now_add=True)


class TransactionRecord(m.Model):
	""" """
	provider = m.ForeignKey(
		'Person', 
		related_name='transaction_records_as_provider'
	)
	receiver = m.ForeignKey(
		'Person', 
		related_name='transaction_records_as_receiver'
	)
	currency = currency_field()
	value = m.IntegerField()
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


class Resolution(m.Model):
	""" """
	provider = m.ForeignKey(
		'Person', 
		related_name='resolutions_as_provider'
	)
	receiver = m.ForeignKey(
		'Person', 
		related_name='resolutions_as_receiver'
	)
	currency = currency_field()
	value = m.IntegerField()
	time_confirmed = m.DateTimeField(auto_now_add=True)


class ExchangeRate(m.Model):
	""" """
	person = m.ForeignKey('Person')
	source_currency = currency_field() 
	dest_currency = currency_field() 
	source_rate = m.IntegerField()
	dest_rate = m.IntegerField()
	time_confirmed = m.DateTimeField(auto_now_add=True)


