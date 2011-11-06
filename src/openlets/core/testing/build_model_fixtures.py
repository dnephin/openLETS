"""
 Build a base set of models to dump to a fixtures file.
"""
import string
import random

import settings
from django.core.management  import setup_environ
setup_environ(settings)

from core.testing.generators import rand_string, rand_bool, rand_date
from core import models, db

letters = list(string.letters)
users = []
currencies = []

def build_users():
	letter = letters.pop(random.randint(0, len(letters) - 1))
	username = 'user%s' % letter
	user = models.User.objects.create_user(
		username, 
		'%s@example.com' % username, 
		password='password'
	)
	user.save()
	users.append(user)
	return user

def build_currency():
	currency = models.Currency(
		name=rand_string(), 
		description=rand_string(200),
		decimal_places=random.randint(0,3)
	)
	currency.save()
	currencies.append(currency)
	return currency

def build_pending_trans(users=users, currencies=currencies):
	"""Build pending transactions. Requires users and currencies to be filled.
	"""
	creator, target = random.sample(users, 2)
	trans_record = models.TransactionRecord(
		creator_person=creator.person,
		target_person=target.person,
		from_receiver=rand_bool(),
		transaction_time=rand_date(),
		notes=rand_string(200),
		currency=random.choice(currencies),
		value=random.randint(1, 200)
	)
	trans_record.save()
	return trans_record

def build_transactions(num=12):
	"""Build completed transactions. Requires users and currencies to be filled.
	"""
	trans_record = build_pending_trans()
	db.confirm_trans_record(trans_record)


builder_counts = [
	(build_users, 5), 
	(build_currency, 3),
	(build_pending_trans, 8),
	(build_transactions, 12),
]

def build_all():
	for builder, count in builder_counts:
		for i in range(count):
			builder()

if __name__ == "__main__":
	build_all()
