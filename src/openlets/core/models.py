from django.db import models as m
from django.contrib.auth.models import User

DATE_FMT = '%Y-%m-%d %H:%M:%S'

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
	persons = m.ManyToManyField(
		'Person',
		through='PersonBalance',
		blank=True,
		related_name='balances'
	)
	currency = currency_field()
	value = m.IntegerField(default=0)
	time_updated = m.DateTimeField(auto_now=True)

	def __unicode__(self):
		credited = debted = None
		for pb in self.personbalance_set.all():
			if pb.credited:
				credited = pb.person
			else:
				debted = pb.person
		return "Balance of %s credited to %s, debt from %s" % (
			self.currency.value_repr(self.value),
			credited,
			debted
		)


class PersonBalance(m.Model):
	"""A join table to link Person one of their Balances."""
	person = m.ForeignKey('Person')
	balance = m.ForeignKey('Balance')
	credited = m.BooleanField()

	def __unicode__(self):
		return "PersonBalance for %s and %s" % (
			self.person,
			self.balance
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
		return "%s Exchange Rate: %s to %s" % (
			self.person,
			self.source_currency.value_repr(self.source_rate),
			self.dest_currency.value_repr(self.dest_rate)
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

	def __unicode__(self):
		confirmed = '-'
		if self.time_confirmed:
			confirmed = self.time_confirmed.strftime(DATE_FMT)
		return "Transaction of %s from %s to %s confirmed at %s" % (
			self.provider_record.currency.value_repr(self.provider_record.value),
			self.provider_record.provider,
			self.provider_record.receiver,
			confirmed
		)


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

	def __unicode__(self):
		return "Transaction Record %s from %s to %s at %s" % (
			self.currency.value_repr(self.value),
			self.provider,
			self.receiver,
			time_created.strftime(DATE_FMT)	
		)


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

	def value_repr(self, value):
		return '%s %s' % (self.value_of(value), self)


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

	def __unicode__(self):
		confirmed = '-'
		if self.time_confirmed:
			confirmed = self.time_confirmed.strftime(DATE_FMT)
		return "Resolution of %s from %s to %s confirmed at %s" % (
			self.currency.value_repr(self.value),
			self.provider,
			self.receiver,
			confirmed
		)

