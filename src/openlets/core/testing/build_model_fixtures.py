"""
 Build a base set of models to dump to a fixtures file.
"""
import string
import random

import settings
from django.core.management  import setup_environ
setup_environ(settings)

from core.testing.generators import rand_string, rand_bool, rand_date, rand_char
from core import models, db

users = []
currencies = []

user_pool = list(string.letters[26:])
currency_pool = list(string.letters[26:])

def build_users():
	letter = rand_char(user_pool)
	username = 'user%s' % letter
	user = models.User.objects.create_user(
		username, 
		'%s@example.com' % username, 
		password='password'
	)
	user.save()
	users.append(user)
	return user

def build_currency(currency_pool=currency_pool):
	letter = rand_char(currency_pool)
	currency = models.Currency(
		name='currency%s' % letter,
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

def build_transaction():
	"""Build completed transactions. Requires users and currencies to be filled.
	"""
	trans_record = build_pending_trans()
	db.confirm_trans_record(trans_record)

def build_exchange_rate(users=users, currencies=currencies):
	"""Build exchange rates."""
	user = random.choice(users)
	currencys, currencyd = random.sample(currencies, 2)
	values, valued = random.randint(0, 200), random.randint(0, 200)
	exchange_rate = models.ExchangeRate(
		person=user.person,
		source_currency=currencys,
		dest_currency=currencyd,
		source_rate=values,
		dest_rate=valued
	)
	exchange_rate.save()
	return exchange_rate

builder_counts = [
	(build_users, 10), 
	(build_currency, 3),
	(build_pending_trans, 25),
	(build_transaction, 100),
	(build_exchange_rate, 10),
]

def build_all():
	for builder, count in builder_counts:
		for i in range(count):
			try:
				builder()
			except Exception, e:
				print "Problem building fixture: %s" % e

if __name__ == "__main__":
	build_all()
