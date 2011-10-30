import itertools

from django.db import models as m
from django.contrib.auth.models import User
from django.db.models.signals import post_save

DATE_FMT = '%Y-%m-%d %H:%M:%S'

currency_field = lambda **kwargs: m.ForeignKey('Currency', related_name='+', **kwargs)

class CurrencyMixin(m.Model):
	"""A MixIn for models with currency.  
	
	Adds a currency field and a value field.
	Adds two properties for getting value.
	"""
	class Meta:
		abstract = True

	currency = currency_field()
	value = m.IntegerField(default=0)

	@property
	def value_repr(self):
		return self.currency.value_repr(self.value)

	@property
	def value_str(self):
		return self.currency.value_of(self.value)


class Person(m.Model):
	""" """
	user = m.OneToOneField(User)
	default_currency = currency_field(null=True, blank=True)

	def __unicode__(self):
		return self.user.username 

	def transaction_records(self):
		return itertools.chain(
			self.transaction_records_as_provider,
			self.transaction_records_as_receiver
		)

def create_person(sender, instance, created, **kwargs):
	"""Create a person for a new user."""
	try:
		default_currency = Currency.objects.get(default=True)
	except Currency.DoesNotExist:
		default_currency = None
	# Raw is set when using loaded (ex: loading test fixtures)
	if created and not kwargs.get('raw'):
		Person.objects.create(user=instance, default_currency=default_currency)
post_save.connect(create_person, sender=User)


class Balance(CurrencyMixin, m.Model):
	"""A balance between two people. 
	"""
	persons = m.ManyToManyField(
		'Person',
		through='PersonBalance',
		blank=True,
		related_name='balances'
	)
	time_updated = m.DateTimeField(auto_now=True)

	def __unicode__(self):
		credited = debted = None
		for pb in self.personbalance_set.all():
			if pb.credited:
				credited = pb.person
			else:
				debted = pb.person
		return "Balance of %s credited to %s, debt from %s" % (
			self.value_repr,
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
			self.provider_record.value_repr,
			self.provider_record.provider,
			self.provider_record.receiver,
			confirmed
		)


class TransactionRecord(CurrencyMixin, m.Model):
	"""
	A record of the transaction submitted by a user. A transaction is not
	official until confirmed by both parties having submitted their own
	transaction record.
	"""
	provider = m.ForeignKey(
		'Person', 
		related_name='transaction_records_as_provider'
	)
	receiver = m.ForeignKey(
		'Person', 
		related_name='transaction_records_as_receiver'
	)
	from_provider = m.BooleanField()
	transaction_time = m.DateTimeField()
	time_created = m.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return "Transaction Record %s from %s to %s at %s" % (
			self.value_repr,
			self.provider,
			self.receiver,
			self.time_created.strftime(DATE_FMT)	
		)

	def set_person(self, person):
		"""
		Store `person` as person in the model, and the other person
		as `other_person`. `person` is most likely the active user performing
		a web request.
		"""
		self.other_person = self.receiver if self.provider == person else self.provider
		self.person = person


class Currency(m.Model):
	""" """
	name = m.CharField(max_length=255)
	description = m.TextField(blank=True)
	decimal_places = m.IntegerField(default=0)
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


class Resolution(CurrencyMixin, m.Model):
	""" """
	provider = m.ForeignKey(
		'Person', 
		related_name='resolutions_as_provider'
	)
	receiver = m.ForeignKey(
		'Person', 
		related_name='resolutions_as_receiver'
	)
	time_confirmed = m.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		confirmed = '-'
		if self.time_confirmed:
			confirmed = self.time_confirmed.strftime(DATE_FMT)
		return "Resolution of %s from %s to %s confirmed at %s" % (
			self.value_repr,
			self.provider,
			self.receiver,
			confirmed
		)

