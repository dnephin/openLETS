"""
Database Acess Layer
"""
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
