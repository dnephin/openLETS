from decimal import Decimal
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


class DictableModel(object):
	"""A mixin that adds a to_dict method to a model."""

	def to_dict(self):
		"""Return a dict of field name to field serializable value."""
		return dict(
			(field.name, self.serializable_value(field.name))
			for field in self._meta.fields
		)


class Person(m.Model):
	"""A person. This model is the auth profile model."""
	user = m.OneToOneField(User)
	default_currency = currency_field(null=True, blank=True)

	def __unicode__(self):
		return self.user.username 

	def transaction_records(self):
		return itertools.chain(
			self.transaction_records_creator,
			self.transaction_records_target
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
post_save.connect(create_person, sender=User, dispatch_uid='create_person_handler')


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
		return "Balance of %s credited to %s, debt from %s" % (
			self.value_repr,
			self.credited,
			self.debted
		)

	@property
	def credited(self):
		return self.personbalance_set.get(credited=True).person
	
	@property
	def debted(self):
		return self.personbalance_set.get(credited=False).person


class PersonBalance(m.Model):
	"""A join table to link Person to one of their Balances."""
	person = m.ForeignKey('Person')
	balance = m.ForeignKey('Balance')
	credited = m.BooleanField()

	def __unicode__(self):
		return "PersonBalance for %s and %s" % (
			self.person,
			self.balance
		)

	@property
	def other_person(self):
		"""Get the person on the other side of this balance."""
		return self.balance.persons.exclude(id=self.person.id).get()

	@property
	def relative_value(self):
		value = self.balance.value
		return self.balance.currency.value_of(value if self.credited else -value)

	@property
	def relative_value_repr(self):
		value = self.balance.value
		value = value if self.credited else -value
		return self.balance.currency.value_repr(value)

	def export_data(self):
		return {
			'person': '%s' %self.other_person,
			'balance': {
				'currency': '%s' % self.balance.currency,
				'value': '%s' % self.relative_value
			},
			'last_updated': self.balance.time_updated.strftime(DATE_FMT)
		}

class ExchangeRate(m.Model):
	"""A rate of exchange between two currencies, offered by a person."""
	person = m.ForeignKey('Person')
	source_currency = currency_field() 
	dest_currency = currency_field() 
	source_rate = m.IntegerField()
	dest_rate = m.IntegerField()
	time_created = m.DateTimeField(auto_now_add=True)

	class Meta:
		unique_together = ('person', 'source_currency', 'dest_currency')

	def __unicode__(self):
		return "%s Exchange Rate: %s to %s" % (
			self.person,
			self.source_repr,
			self.dest_repr
		)

	@property
	def source_repr(self):
		return self.source_currency.value_repr(self.source_rate)

	@property
	def dest_repr(self):
		return self.dest_currency.value_repr(self.dest_rate)

	@property
	def source_value(self):
		return self.source_currency.value_of(self.source_rate)

	@property
	def dest_value(self):
		return self.dest_currency.value_of(self.dest_rate)

	def export_data(self):
		return {
			'source': {
				'currency': '%s' % self.source_currency,
				'rate': '%s' % self.source_value
			},
			'destination': {
				'currency': '%s' % self.dest_currency,
				'rate': '%s' % self.dest_value
			},
			'time_created': self.time_created.strftime(DATE_FMT)
		}


class Transaction(m.Model):
	"""A transaction between two people."""
	time_confirmed = m.DateTimeField(auto_now_add=True, null=True, blank=True)

	def __unicode__(self):
		confirmed = '-'
		if self.time_confirmed:
			confirmed = self.time_confirmed.strftime(DATE_FMT)
		return "Transaction of %s from %s to %s confirmed at %s" % (
			self.provider_record.value_repr,
			self.provider,
			self.receiver,
			confirmed
		)

	@property
	def currency(self):
		"""Get the currency of a resolved transaction."""
		if not self.time_confirmed:
			raise ValueError("Transaction not yet resolved.")
		return self.transaction_records.all()[0].currency

	@property
	def value(self):
		if not self.time_confirmed:
			raise ValueError("Transaction not yet resolved.")
		return self.transaction_records.all()[0].value

	@property
	def persons(self):
		"""Get the persons participating in the transaction."""
		return [record.person for record in self.transaction_records.all()]

	@property
	def provider_record(self):
		return self.transaction_records.get(from_receiver=False)

	@property
	def receiver_record(self):
		return self.transaction_records.get(from_receiver=True)

	@property
	def provider(self):
		return self.provider_record.creator_person

	@property
	def receiver(self):
		return self.receiver_record.creator_person


class TransactionRecord(DictableModel, CurrencyMixin, m.Model):
	"""
	A record of the transaction submitted by a user. A transaction is not
	complete until confirmed by both parties having submitted their own
	transaction record.
	"""
	transaction = m.ForeignKey(
		'Transaction', 
		related_name='transaction_records',
		null=True,
		blank=True
	)
	creator_person = m.ForeignKey(
		'Person', 
		related_name='transaction_records_creator'
	)
	target_person = m.ForeignKey(
		'Person', 
		related_name='transaction_records_target',
	)
	from_receiver = m.BooleanField()
	rejected = m.BooleanField(default=False)
	transaction_time = m.DateTimeField()
	time_created = m.DateTimeField(auto_now_add=True)
	notes = m.TextField(null=True, blank=True)

	def __unicode__(self):
		return "Transaction Record (by %s)  %s from %s to %s at %s" % (
			self.creator_person,
			self.value_repr,
			self.provider,
			self.receiver,
			self.time_created.strftime(DATE_FMT)	
		)

	@property
	def provider(self):
		"""Returns the person who is the provider in the transaction."""
		return self.creator_person if not self.from_receiver else self.target_person

	@property
	def receiver(self):
		return self.creator_person if self.from_receiver else self.target_person

	@property
	def status(self):
		if self.rejected:
			return 'rejected'
		trans = self.transaction
		return 'confirmed' if trans and trans.time_confirmed else 'pending'

	@property
	def transaction_type(self):
		"""The type of transaction relative to the user who created this record."""
		return 'charge' if self.from_receiver else 'payment'

	@property
	def targets_transaction_type(self):
		"""The type of transaction relative to the target user."""
		return 'payment' if self.from_receiver else 'charge'

	@property
	def other_transaction_record(self):
		if not self.transaction:
			raise ValueError("No transaction yet.")
		return self.transaction.transaction_records.exclude(id=self.id).get()

	def export_data(self):
		time_confirmed = None
		if self.status == 'confirmed':
			time_confirmed = self.transaction.time_confirmed.strftime(DATE_FMT)

		return {
			'person': '%s' % self.target_person,
			'transfer_type': 'Transaction',
			'status': self.status,
			'transaction_type': self.transaction_type,
			'amount': {
				'value': '%s' % self.value_str,
				'currency': '%s' % self.currency
			},
			'time': self.transaction_time.strftime(DATE_FMT),
			'time_confirmed': time_confirmed,
		}


class Currency(m.Model):
	"""A currency that can be used for exchange."""
	name = m.CharField(max_length=255)
	description = m.TextField(blank=True)
	decimal_places = m.IntegerField(default=0)
	default = m.BooleanField(default=False)
	time_created = m.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return self.name

	def value_of(self, value):
		"""The decimal value of 'value' in this currency."""
		if not self.decimal_places:
			return Decimal(value)
		return Decimal(value) / (10 ** self.decimal_places)

	def value_repr(self, value):
		return ('%%.%df %%s' % self.decimal_places) % (self.value_of(value), self)


class Resolution(CurrencyMixin, m.Model):
	"""A resolution of debts between a circle of users."""
	persons = m.ManyToManyField(
		'Person',
		through='PersonResolution',
		blank=True,
		related_name='resolutions'
	)
	action_id = m.IntegerField()
	time_confirmed = m.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		confirmed = '-'
		if self.time_confirmed:
			confirmed = self.time_confirmed.strftime(DATE_FMT)
		return "Resolution of %s between %s confirmed at %s" % (
			self.value_repr,
			", ".join('%s' % p for p in self.persons.all()),
			confirmed
		)

	@property
	def provider(self):
		return self.personresolution_set.get(credited=False).person
		
	@property
	def receiver(self):
		return self.personresolution_set.get(credited=True).person


class PersonResolution(m.Model):
	"""A join table to link Person to one of their Resolutions."""
	person = m.ForeignKey('Person')
	resolution = m.ForeignKey('Resolution')
	credited = m.BooleanField()

	def __unicode__(self):
		return "PersonResolution for %s and %s" % (
			self.person,
			self.resolution
		)

	@property
	def other_person(self):
		"""Get the person on the other side of this balance."""
		return self.resolution.persons.exclude(id=self.person.id).get()

	@property
	def relative_value(self):
		value = self.resolution.value
		return self.resolution.currency.value_of(value if self.credited else -value)

	@property
	def relative_value_repr(self):
		value = self.resolution.value
		value = value if self.credited else -value
		return self.resolution.currency.value_repr(value)

	@property
	def transaction_time(self):
		return self.resolution.time_confirmed

	@property
	def transaction_type(self):
		"""The type of transaction relative to this person."""
		return 'charge' if self.credited else 'payment'

	def export_data(self):
		return {
			'person': '%s' % self.other_person,
			'transfer_type': 'Resolution',
			'transaction_type': self.transaction_type,
			'amount': {
				'value': '%s' % self.resolution.value_str,
				'currency': '%s' % self.resolution.currency
			},
			'time': self.transaction_time.strftime(DATE_FMT),
		}
