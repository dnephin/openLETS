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
		
