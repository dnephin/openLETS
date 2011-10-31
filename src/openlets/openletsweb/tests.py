
"""
 Unittests!
"""
import functools
from django.test import TestCase 
from django import forms as djforms

from openletsweb import forms
from core import models

class FormTestCase(TestCase):
	form_class = None
	form = None

	def setUp(self):
		if self.form_class:
			self.form = self.form_class()
			self.form.cleaned_data = {}
			self.form._errors = {}

	def _clean_field(self, name, raw_value):
		self.form.cleaned_data[name] = raw_value
		return getattr(self.form, 'clean_%s' % name)()


class TransactionRecordFormTestCase(FormTestCase):
	form_class = forms.TransactionRecordForm

	def setUp(self):
		super(TransactionRecordFormTestCase, self).setUp()
		self.currency = models.Currency(name='Test Currency', decimal_places=3, default=True)
		self.currency.save()
		self.form.cleaned_data['currency'] = self.currency

		# TODO: the signal to create person is breaking this
#		self.user = models.User.objects.create_user('testa', 'test@example.com', 'p')

	def tearDown(self):
		super(TransactionRecordFormTestCase, self).tearDown()
		self.currency.delete()
#		self.user.person.delete()
#		self.user.delete()
	
	def test_clean_value(self):
		"""Test cleaning value."""
		clean = functools.partial(self._clean_field, 'value')
		asr = functools.partial(self.assertRaises, djforms.ValidationError, clean)
		for input, result in [
			('1.2', (1, 2)),
			('999', (999,)),
			('45.12345', (45,12345)),
			('0.0001', (0, 0001)),
		]:
			self.assertEqual(clean(input), result)

		asr('1.2.1')
		asr('a.01')
		asr('.01')
		asr('345.')

	def test_clean(self):
		"""Testing clean of value with currency."""
		def clean_with_value(value):
			self.form.cleaned_data['value'] = value
			cleaned_data = self.form.clean()
			return cleaned_data.get('value')

		for input, result in [
			((1, 2), 1200),
			((999,), 999000),
			((45, 123), 45123),
			((12, 12), 12120)
		]:
			self.assertEqual(clean_with_value(input), result)
		assert not self.form._errors.get('value')

		clean_with_value((0, 1234))
		assert self.form._errors['value']

	def test_save(self):
		"""Test saving the model from a form."""
		form = self.form_class({
			'value': 12000,
			'currency': self.currency.id,
			'target_person': 45,
		})
#		form.save(self.user)
		# TODO: test from_provider and value are set
