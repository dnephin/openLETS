"""
Database Acess Layer
"""
import datetime
import itertools
import operator

from django.db.models import Q
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist

from core import models

def get_balance(persona, personb, currency=None):
	"""Load a balance between two persons. 
	"""
	return (models.PersonBalance.objects
		.select_related(
			'balance'
			'balance__persons'
		)
		.get(
			person=persona,
			balance__persons=personb,
			balance__currency=currency
		).balance
	)

def get_balances(user):
	"""Get the list of balances for a user. Filter out any where the value is
	back to 0.
	"""
	return models.PersonBalance.objects.filter(
		person=user.person,
	).exclude(
		balance__value=0
	)

def get_pending_trans_for_user(user):
	"""Get pending transactions for a user which were
	created by some other user, and need to be accepted.
	"""
	return models.TransactionRecord.objects.filter(
		target_person=user.person,
		transaction__isnull=True
	)

def get_recent_trans_for_user(user, days=10):
	"""Get recent transaction records for the user.  These transaction records
	may be confirmed.
	"""
	earliest_day = datetime.date.today() - datetime.timedelta(days)
	return models.TransactionRecord.objects.filter(
		creator_person=user.person,
		time_created__gte=earliest_day
	).order_by('-time_created')

# TODO: tests
def get_transfer_history(user, filters):
	"""Get a list of all transactions and resolutions for the user filtered
	by form filters.
	"""
	query_sets = []
	resolution_query, trans_query = [], []
	now = datetime.datetime.now()

	def conv(key, trans, resolution, coerce_val=None):
		"""Helper to setup filters for both tables."""
		val = filters.get(key)
		if not val:
			return
		if coerce_val:
			val = coerce_val(val)
		if trans:
			trans_query.append((trans, val))
		if resolution:
			resolution_query.append((resolution, val))

	# Setup filters 
	transfer_type = filters.get('transfer_type')
	conv('person', 'target_person', 'resolution__persons')
	conv('transaction_type', 'from_receiver', 'credited', lambda x: x == 'charge')
	conv('currency', 'currency', 'resolution__currency')

	conv('status',
		'transaction__time_confirmed__isnull',
		'resolution__time_confirmed__isnull',
		lambda x: x == 'pending'
	)

	conv('transaction_time', 
		'transaction_time__gt', 
		'resolution__time_confirmed__gt',
		lambda d: now - datetime.timedelta(days=d)
	)

	conv('confirmed_time',
		'transaction__time_confirmed__gt',
		'resolution__time_confirmed__gt',
		lambda d: now - datetime.timedelta(days=d)
	)

	# Query Transactions
	if not transfer_type or transfer_type == 'transaction':
		query_sets.append(models.TransactionRecord.objects.filter(
			creator_person=user.person,
			**dict(trans_query)
		))

	# Query Resolutions
	if not transfer_type or transfer_type == 'resolution':
		query_sets.append(models.PersonResolution.objects.filter(
			person=user.person,
			**dict(resolution_query)
		))

	# Merge results
	return sorted(
		itertools.chain.from_iterable(query_sets), 
		key=operator.attrgetter('transaction_time')
	)


def get_trans_record_for_user(trans_record_id, user):
	"""Get a transaction record for a user."""
	return models.TransactionRecord.objects.get(
		id=trans_record_id,
		target_person=user.person
	)

@transaction.commit_on_success
def confirm_trans_record(trans_record):
	"""Confirm a transaction record."""
	# Build and save matching record
	confirm_record = models.TransactionRecord(
		creator_person=trans_record.target_person,
		target_person=trans_record.creator_person,
		from_receiver=not trans_record.from_receiver,
		currency=trans_record.currency,
		transaction_time=trans_record.transaction_time,
		value=trans_record.value
	)
	transaction = models.Transaction()
	confirm_record.transaction = trans_record.transaction = transaction

	transaction.save()
	confirm_record.save()
	trans_record.save()

	# Update the balance, or create a new one
	update_balance(
		trans_record, 
		trans_record.provider,
		trans_record.receiver
	)


# TODO: I'd like this to be able to use the properties of a transfer object
# TODO: tests!
def update_balance(currency_type, provider, receiver):
	"""Update or create a balance between two users for a currency. Should be
	called from a method that was already created a transfer.
	"""
	try:
		balance = get_balance(provider, receiver, currency=currency_type.currency)
	except ObjectDoesNotExist:
		return new_balance(currency_type, provider, receiver)

	# Establish the direction of the transfer
	if provider == balance.debted:
		balance.value += currency_type.value
		balance.save()
		return balance

	balance_value = balance.value - currency_type.value
	if (balance_value) < 0:
		balance.value = abs(balance_value)
		for personbalance in balance.persons:
			personbalance.credited = not personbalance.credited

	balance.save()
	# TODO: does this cascade to the personbalance ?
	return balance


# TODO: complete this
def new_balance(currency_type, provider, receiver):
	balance = models.Balance(
		currency=currency_type.currency, 
		value=currency_type.value
	)
	balance.save()
	personbalancea = models.PersonBalance(
		person=provider,
		credited=False,
		balance_id=balance.id
	)
	personbalanceb = models.PersonBalance(
		person=receiver,
		credited=True,
		balance_id=balance.id
	)
	personbalancea.save()
	personbalanceb.save()
	return balance
	
