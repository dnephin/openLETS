"""
 Forms for openletsweb.
"""
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import forms as auth_forms
from django import forms

from openlets.core import models
from openlets.openletsweb.forms.base import *

__all__ = [
	'TransactionRecordForm',
	'TransferListForm',
	'PersonForm',
	'ExchangeRateForm',
	'UserCreateForm',
	'UserEditForm',
	'LoginForm',
	'PasswordChangeForm',
]

class TransactionRecordForm(BaseFormMixin, forms.ModelForm):
	"""A Form for creating new TransactionRecord objects."""

	class Meta:
		model = models.TransactionRecord
		fields = (
			'transaction_time', 
			'target_person', 
			'from_receiver',
			'currency',
			'value',
			'notes',
		)
		widgets = {
			'transaction_time': forms.TextInput(attrs={'class': 'medium'}),
			'notes': forms.Textarea(attrs={'rows': 7, 'class': 'span4'}),
		}

	_parts = {
		'main_col': [
			'transaction_time', 'from_receiver', 'target_person', 'currency', 'value'
		],
		'notes_col': ['notes']
	}

	from_receiver =  forms.TypedChoiceField(
		label="Type",
		choices=[
			('payment', 'Payment'),
			('charge', 'Charge')
		],
		coerce=lambda o: o == 'charge',
		widget=forms.RadioSelect(renderer=widgets.UnstyledRadioRenderer),
		initial='payment'
	)
	value = CurrencyValueField()

	def clean(self):
		"""Clean the form. Ensure value makes sense for the currency."""
		cleaned_data = self.cleaned_data
		if self._errors:
			return cleaned_data

		value, error = currency_clean_helper(
			cleaned_data['currency'], cleaned_data['value'])
		if error:
			self._errors.setdefault('value', []).append(error)
			return cleaned_data
		cleaned_data['value'] = value
		return cleaned_data

	def save(self, active_user, commit=True):
		"""Save the model. Make sure persons are assigned to correct
		field.
		"""
		trans_rec = super(TransactionRecordForm, self).save(commit=False)
		data = self.cleaned_data

		trans_rec.creator_person = active_user.person
		# TODO: cleaner error message
		assert trans_rec.target_person != active_user.person

		if commit:
			return trans_rec.save()
		return trans_rec


class TransferListForm(BaseFormMixin, forms.Form):
	"""A form for validating filters for viewing lists of transactions
	and resolutions.
	"""
	day_field_attrs = {'data-min': 1, 'data-max': 365, 'placeholder': 'All'}

	_parts = {
		'radios': ['transfer_type', 'transaction_type', 'status'],
		'left_col': ['person', 'currency', 'transaction_time', 'confirmed_time']
	}

	person = forms.ModelChoiceField(models.Person.objects.all(), required=False)
	transfer_type = forms.ChoiceField(
		choices=[
			('', 'All'),
			('transaction','Transactions'),
			('resolution','Resolutions'),
		],
		required=False,
		widget=forms.RadioSelect(renderer=widgets.UnstyledRadioRenderer),
	)
	transaction_type = forms.ChoiceField(
		choices=[
			('', 'All'),
			('payment', 'Payments'),
			('charge', 'Charges'),
		],
		required=False,
		widget=forms.RadioSelect(renderer=widgets.UnstyledRadioRenderer),
	)
	status = forms.ChoiceField(
		choices=[
			('', 'All'),
			('pending', 'Pending'),
			('confirmed', 'Confirmed')
		],
		required=False,
		widget=forms.RadioSelect(renderer=widgets.UnstyledRadioRenderer),
	)


	# Transaction time in days
	transaction_time = forms.IntegerField(
		min_value=1,
		max_value=365,
		required=False,
		initial=30,
		widget=widgets.JUISlider(attrs=day_field_attrs)
	)
	# Confirmed Time in days
	confirmed_time = forms.IntegerField(
		min_value=1,
		max_value=365,
		required=False,
		initial=100,
		widget=widgets.JUISlider(attrs=day_field_attrs)
	)
	currency = forms.ModelChoiceField(models.Currency.objects.all(), required=False)


class PersonForm(BaseFormMixin, forms.ModelForm):
	"""A form to edit Person details."""

	class Meta:
		model = models.Person
		fields = ('default_currency',)


class ExchangeRateForm(BaseFormMixin, forms.ModelForm):
	"""A form to create or edit Exchange Rates."""

	class Meta:
		model = models.ExchangeRate
		fields = (
			'source_currency', 'source_rate',
			'dest_currency', 'dest_rate'
		)

	source_rate = CurrencyValueField()
	dest_rate = CurrencyValueField()

	def clean(self):
		"""Clean the form. Ensure value makes sense for the currency."""
		cleaned_data = self.cleaned_data
		if self._errors:
			return cleaned_data

		if cleaned_data['source_currency'] == cleaned_data['dest_currency']:
			self._errors['source_currency'] = [
				"Source and destination currency must be different."
			]

		source_value, source_error = currency_clean_helper(
			cleaned_data['source_currency'], 
			cleaned_data['source_rate']
		)
		dest_value, dest_error = currency_clean_helper(
			cleaned_data['dest_currency'], 
			cleaned_data['dest_rate']
		)
		if source_error:
			self._errors.setdefault('source_rate', []).append(source_error)
		if dest_error:
			self._errors.setdefault('dest_rate', []).append(dest_error)
		if self.errors:
			return cleaned_data
	
		cleaned_data['source_rate'] = source_value
		cleaned_data['dest_rate'] = dest_value
		return cleaned_data

	# TODO: handle duplicate exchange rates (see model unique constraint)
	def save(self, active_user, commit=True):
		model = super(ExchangeRateForm, self).save(commit=False)
		model.person = active_user.person
		if commit:
			return model.save()
		return model


class UserCreateForm(BaseFormMixin, forms.ModelForm):
	"""A form to create a new user."""

	class Meta:
		model = models.User
		fields = ('username', 'first_name', 'last_name', 'email', 'password')

	username = PlaceholderChar(max_length=30)
	first_name = PlaceholderChar(max_length=30)
	last_name = PlaceholderChar(max_length=30)
	email = PlaceholderEmail()
	password = PlaceholderChar(widget=widgets.PlaceholderPasswordInput)


class UserEditForm(BaseFormMixin, forms.ModelForm):
	"""A form to edit user details."""

	class Meta:
		model = models.User
		fields = ('username', 'first_name', 'last_name', 'email')


class LoginForm(BaseFormMixin, auth_forms.AuthenticationForm):
	
	username = PlaceholderChar(max_length=30)
	password = PlaceholderChar(widget=widgets.PlaceholderPasswordInput) 

class PasswordChangeForm(BaseFormMixin, auth_forms.PasswordChangeForm):
	pass
