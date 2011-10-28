from django.db import models as m
from django.contrib.auth.models import User


currency_field = lambda: m.ForeignKey('Currency', related_name='+')


class Person(m.Model):
	""" """
	user = m.OneToOneField(User)
	default_currency = currency_field()

	def __unicode__(self):
		return self.user.username 


class Balance(m.Model):
	"""A balance between two people.
	"""
	persons = m.ManyToManyField('Person', related_name='balances', blank=True)
	credited_person = m.ForeignKey('Person')
	currency = currency_field()
	value = m.IntegerField(default=0)

	def __unicode__(self):
		return "Balance of %s credited to %s between %s" % (
			self.currency.value_of(self.value),
			self.credited_person,
			','.join('%s' % person for person in self.persons.all())
		)


class ExchangeRate(m.Model):
	""" """
	person = m.ForeignKey('Person')
	source_currency = currency_field() 
	dest_currency = currency_field() 
	source_rate = m.IntegerField()
	dest_rate = m.IntegerField()
	time_confirmed = m.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return "%s Exchange Rate: %s %s to %s %s" % (
			self.person,
			self.source_currency.value_of(self.source_rate),
			self.source_currency,
			self.dest_currency.value_of(self.dest_rate),
			self.dest_currency
		)

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
	time_confirmed = m.DateTimeField(auto_now_add=True, null=True, blank=True)


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
	transaction_time = m.DateTimeField()
	time_created = m.DateTimeField(auto_now_add=True)


class Currency(m.Model):
	""" """
	name = m.CharField(max_length=255)
	description = m.TextField(blank=True)
	decimal_places = m.IntegerField(default=0)
	creator = m.ForeignKey(Person, null=True, blank=True)
	default = m.BooleanField(default=False)
	time_created = m.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return self.name

	def value_of(self, value):
		"""The float value of 'value' in this currency."""
		if not self.decimal_places:
			return float(value)
		return float(value) / (self.decimal_places * 10)


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


