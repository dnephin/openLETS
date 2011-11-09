from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import forms as auth_forms
from django import forms
from openlets.core import models
from openlets.openletsweb import widgets


class PlainForm(object):
	"""Mixin for adding an as_plain render method."""

	def as_plain(self):
		"""Render the form without labels and help text."""
		return self._html_output(
			normal_row = u'<p%(html_class_attr)s>%(field)s</p>',
			error_row = u'%s',
			row_ender = '</p>',
			help_text_html = u'%s',
			errors_on_separate_row = True)

class PlaceholderField(object):
	"""A mixin for fields that uses placeholder for label."""

	def widget_attrs(self, widget):
		attrs = super(PlaceholderField, self).widget_attrs(widget) or {}
		attrs['placeholder'] = self.label
		return attrs

class PlaceholderChar(PlaceholderField, forms.CharField):
	widget = widgets.PlaceholderTextInput

class PlaceholderEmail(PlaceholderField, forms.EmailField):
	widget = widgets.PlaceholderTextInput


class TransactionRecordForm(forms.ModelForm):
	"""A Form for creating new TransactionRecord objects."""

	class Meta:
		model = models.TransactionRecord
		fields = ('currency', 'transaction_time', 'target_person', 'notes')

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
	value = forms.CharField(max_length=200)

	def clean_value(self):
		"""Clean a value. Ensure that the value is numeric."""
		value = self.cleaned_data['value']
		value_parts = value.split('.')
		if len(value_parts) > 2:
			raise forms.ValidationError("Unknown number %s" % (value))
		for part in value_parts:
			if not part.isdigit():
				raise forms.ValidationError("Unknown number %s" % (value))
		return tuple(int(p) for p in value_parts)

	def clean(self):
		"""Clean the form. Ensure value makes sense for the currency."""
		cleaned_data = self.cleaned_data
		if self._errors:
			return cleaned_data
		currency = cleaned_data['currency']
		value = cleaned_data['value']

		whole = value[0]
		frac = str(value[1]) if len(value) == 2 else None
		if frac and len(frac) > currency.decimal_places:
			self._errors['value'] = [
				"Too many decimal places (%s) for currency %s" % (
					len(frac), currency)
			]
			return cleaned_data

		if not frac:
			frac = '0' * currency.decimal_places
		elif len(frac) < currency.decimal_places:
			frac += '0' * (currency.decimal_places - len(frac))

		cleaned_data['value'] = int(str(whole) + frac)
		return cleaned_data

	def save(self, active_user, commit=True):
		"""Save the model. Make sure persons are assigned to correct
		field.
		"""
		trans_rec = super(TransactionRecordForm, self).save(commit=False)
		data = self.cleaned_data

		trans_rec.value = data['value']
		trans_rec.from_receiver = data['from_receiver']
		trans_rec.creator_person = active_user.person

		if commit:
			return trans_rec.save()
		return trans_rec


class TransferListForm(forms.Form):
	"""A form for validating filters for viewing lists of transactions
	and resolutions.
	"""

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
		initial=30
	)
	# Confirmed Time in days
	confirmed_time = forms.IntegerField(
		min_value=1, 
		max_value=365, 
		required=False, 
	)
	currency = forms.ModelChoiceField(models.Currency.objects.all(), required=False)


class PersonForm(forms.ModelForm):
	"""A form to edit Person details."""

	class Meta:
		model = models.Person
		fields = ('default_currency',)


class ExchangeRateForm(forms.ModelForm):
	"""A form to create or edit Exchange Rates."""

	class Meta:
		model = models.ExchangeRate
		exclude = ('person', 'time_created')

	def save(self, active_user, commit=True):
		model = super(ExchangeRateForm, self).save(commit=False)
		model.person = active_user.person
		if commit:
			return model.save()
		return model


class UserCreateForm(forms.ModelForm, PlainForm):
	"""A form to create a new user."""

	class Meta:
		model = models.User
		fields = ('username', 'first_name', 'last_name', 'email', 'password')

	username = PlaceholderChar(max_length=30)
	first_name = PlaceholderChar(max_length=30)
	last_name = PlaceholderChar(max_length=30)
	email = PlaceholderEmail()
	password = PlaceholderChar(widget=widgets.PlaceholderPasswordInput)


class UserEditForm(forms.ModelForm, PlainForm):
	"""A form to edit user details."""

	class Meta:
		model = models.User
		fields = ('username', 'first_name', 'last_name', 'email')


class LoginForm(auth_forms.AuthenticationForm, PlainForm):
	
	username = PlaceholderChar(max_length=30)
	password = PlaceholderChar(widget=widgets.PlaceholderPasswordInput) 
