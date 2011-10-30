"""
 Unittests!
"""
from django.test import TestCase 

from core import db

class DBTestCase(TestCase):
	fixtures = ['testing/base.json']
	
	def test_get_balance(self):
		balance = db.get_balance(2,3)
		self.assertEqual(balance.value, 14)
		self.assertEqual(set(u.id for u in balance.persons.all()), set([2,3]))

	def test_get_pending_trans_for_user(self):
		user = db.models.User.objects.get(id=5)
		records = list(db.get_pending_trans_for_user(user))
		self.assertEqual(len(records), 2)
		for record in records:
			self.assertRaises(
				db.models.Transaction.DoesNotExist,
				lambda: record.provider_transaction
			)
			self.assertRaises(
				db.models.Transaction.DoesNotExist,
				lambda: record.receiver_transaction
			)
