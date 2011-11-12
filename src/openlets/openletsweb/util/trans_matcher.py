"""
 Utilities for matching transaction records.
"""

# TODO: tests
def find_similar(users_pending_trans, other_user_trans_record):
	"""Find a similar trans_record from users_pending_trans that matches the 
	other_user_trans_record. The creator of other_user_trans_record should 
	match the target in users_pending_trans records.
	"""
	def person_match(trans_record):
		return trans_record.creator_person == other_user_trans_record.target_person

	def currency_match(trans_record):
		return trans_record.currency == other_user_trans_record.currency

	def delta_transaction_time(trans_record):
		return abs(
			trans_record.transaction_time - other_user_trans_record.transaction_time
		)

	candidates = filter(person_match, users_pending_trans)
	if not candidates:
		return None

	candidates = filter(currency_match, candidates) or candidates
	if len(candidates) == 1:
		return candidates[0]

	return sorted(candidates, key=delta_transaction_time)[0]

