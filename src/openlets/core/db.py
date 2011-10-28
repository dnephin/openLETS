"""
Database Acess Layer
"""
from openletsweb import models

def get_balance(usera, userb):
	"""Load a balance between two users. Eager loads the currency and users
	associated with the balance.
	"""
	return models.Person.objects.select_related(
		'balances',
		'balances__currency',
		'balances__persons'
	).filter(
		balances__persons=userb,
		id=usera
	)
	
