"""
 Unittests!
"""
from decimal import Decimal
from django.test import TestCase 

from core import db
from core import models

class DBTestCase(TestCase):
	fixtures = ['testing/base.json']
	
	def test_get_balance(self):
		balance = db.get_balance(2,3)
		self.assertEqual(balance.value, 14)
		self.assertEqual(set(u.id for u in balance.persons.all()), set([2,3]))

	def test_get_pending_trans_for_user(self):
		user = models.User.objects.get(id=5)
		records = list(db.get_pending_trans_for_user(user))
		self.assertEqual(len(records), 2)
		for record in records:
			self.assertRaises(
				models.Transaction.DoesNotExist,
				lambda: record.provider_transaction
			)
			self.assertRaises(
				models.Transaction.DoesNotExist,
				lambda: record.receiver_transaction
			)

class CurrencyModelTestCase(TestCase):

	def setUp(self):
		self.currency_name = 'a'

	def _create_with_places(self, num_places):
		return models.Currency(
			name=self.currency_name,
			decimal_places=num_places
		)
	
	def test_value_of(self):
		value = '1234'
		for places, result in enumerate([
			'1234',
			'123.4',
			'12.34',
			'1.234',
			'0.1234',
			'0.01234'
		]):
			c = self._create_with_places(places)
			self.assertEqual(c.value_of(value), Decimal(result))

	def test_value_repr(self):
		value = '100000'
		for places, result in enumerate([
			'100000',
			'10000.0',
			'1000.00',
			'100.000',
			'10.0000',
			'1.00000',
			'0.100000'
		]):
			c = self._create_with_places(places)
			rep = '%s %s' % (result, self.currency_name)
			self.assertEqual(c.value_repr(value), rep)

