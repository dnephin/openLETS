"""
Database Acess Layer
"""
import datetime
import itertools
import operator
from core import models

def get_balance(persona, personb):
	"""Load a balance between two persons. 
	"""
	return (models.PersonBalance.objects
		.select_related(
			'balance'
			'balance__persons'
		)
		.get(
			person=persona,
			balance__persons=personb
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
		provider_transaction__isnull=True,
		receiver_transaction__isnull=True
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
def get_trans_history(user, filters):
	"""Get a list of all transactions and resolutions for the user filtered
	by filters.
	"""
	query_sets = []
	resolution_filters, trans_filters = {}, {}
	now = datetime.datetime.now()

	def conv(key, trans_key, resolution_key, coerce_val=None):
		"""Helper to setup filters for both tables."""
		val = filters.get(key)
		if not val:
			return
		if coerce_val:
			val = coerce_val(val)
		if trans_key:
			trans_filters[trans_key] = val
		if resolution_key:
			resolution_filters[resolution_key] = val


	# Setup filters 
	event_type = filters.get('event_type')
	conv('person', 'target_person', 'resolution__persons')

	# TODO: transaction type
	#if 'transaction_type' in filters:
	#	trans_type = filters['transaction_type']

	# TODO: status
	conv('transaction_time', 
		'transaction_time__gt', 
		'resolution__time_confirmed__gt',
		lambda d: now - datetime.timedelta(days=d)
	)
	# TODO: use Q objects for transaction
	conv('confirmed_time',
		None,
		'resolution__time_confirmed__gt',
		lambda d: now - datetime.timedelta(days=d)
	)
	conv('currency', 'currency', 'resolution__currency')

	# Query Transactions
	if not event_type or event_type == 'transaction':
		query_sets.append(models.TransactionRecord.objects.filter(
			creator_person=user.person,
			**trans_filters
		))

	# Query Resolutions
	if not event_type or event_type == 'resolution':
		query_sets.append(models.PersonResolution.objects.filter(
			person=user.person,
			**resolution_filters
		))

	# Merge results
	return sorted(
		itertools.chain.from_iterable(query_sets), 
		key=operator.attrgetter('transaction_time')
	)
