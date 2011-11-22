"""
 Resolve balances between users.
"""
import logging

from optparse import OptionParser
from openlets.core import models, db

class BalanceResolver(object):

	def setup_options(self):
		self.option_parser = parser = OptionParser()
		parser.add_option('-l', '--chain-limit', 
			dest="chain_limit",
			help="Limit the number of users in a resolution chain.",
			default=5
		)

	def load_options(self):
		self.options, self.args = self.option_parser.parse_args()

	def setup_logging(self):
		self.log = logging.getLogger('BalanceResolver')
		self.log.setLevel(logging.DEBUG)
		self.log.addHandler(logging.StreamHandler())

	def get_balance_chain(self, persons, target_balance, depth=0):
		"""Find a balance from persons with target_person which is credited
		according to `credited`. If a balance is not found recursively calls
		itself with all of the persons for the last set of balances.
		"""
		if depth > self.options.chain_limit:
			return None
		if not persons:
			return None

		credited = not target_balance.credited
		target_person = target_balance.person
		currency = target_balance.balance.currency

		mirrored_balances = db.get_balances_many(persons, currency, credited)
		for mirrored_balance in mirrored_balances:
			if target_person == mirrored_balance.other_person:
				return [mirrored_balance]

		mirrored_persons = set(pb.other_person for pb in mirorred_balances)
		balance_chain = self.get_balance_chain(
			mirrored_persons, 
			target_balance, 
			depth + 1
		)
		if not balance_chain:
			return

		# Find the balance in this context which links back to the original
		# balance
		link_person = balance_chain[-1].person
		for mirrored_balance in mirrored_balances:
			if mirrored_balance.person == link_person:
				balance_chain.append(mirrored_balance)
				return balance_chain

	def resolve_balances(self, balances):
		for balance in balances:
			balance_chain = self.get_balance_chain(
				[balance.other_person], 
				balance
			)
			if balance_chain:
				self.resolve(balance_chain)
	
	def resolve(self, balance_chain):
		self.log.info("Resolving %s" % balance_chain)
		# TODO:

	def run(self):
		"""Run over all users and find chains of balances which will resolve
		down to lower balances.
		"""
		users = models.User.objects.filter(is_active=True).all()
		for user in users:
			balances = db.get_balances(user)
			self.resolve_balances(balances)
		
	def start(self):
		self.setup_options()
		self.load_options()
		self.setup_logging()
		self.run()


if __name__ == "__main__":
	BalanceResolver().start()
