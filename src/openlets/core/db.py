"""
Database Acess Layer
"""
import datetime
import itertools
from core import models

def get_balance(usera, userb):
	"""Load a balance between two users. 
	"""
	return (models.PersonBalance.objects
		.select_related(
			'balance'
			'balance__persons'
		)
		.get(
			person=usera,
			balance__persons=userb
		).balance
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
