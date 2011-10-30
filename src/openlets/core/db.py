"""
Database Acess Layer
"""
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
	q = models.TransactionRecord.objects
	records = itertools.chain(
		q.filter(
			from_provider=False,
			provider=user.person,
			provider_transaction__isnull=True
		),
		q.filter(
			from_provider=True,
			receiver=user.person,
			receiver_transaction__isnull=True
		).all()
	)
	person = user.person
	for record in records:
		record.set_person(person)
		yield record

