"""
 Random value generators for model builders.
"""

import random
import string
from datetime import datetime, timedelta

def rand_string(length=10, letters=string.letters):
	letters = list(letters)
	if length > 25:
		letters.extend([' ', '.', ',', '-', '!', '\n'])

	chars = []
	for i in range(length):
		chars.append(random.choice(letters))
	return ''.join(chars)

def rand_bool():
	return random.choice([True, False])

def rand_date(min_days_ago=1, max_days_ago=100):
	days = random.randint(min_days_ago, max_days_ago)
	return datetime.now() - timedelta(days, random.randint(0, 60*60*24))

letters = list(string.letters)
def rand_char(pool=letters):
	return pool.pop(random.randint(0, len(pool) - 1))
	
