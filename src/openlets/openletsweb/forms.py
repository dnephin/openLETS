from django import forms
from openlets.core import models


class TransactionRecordForm(forms.ModelForm):
	"""A Form for creating new TransactionRecord objects."""

	class Meta:
		model = models.TransactionRecord
		fields = ('currency', 'transaction_time', 'target_person')

	from_receiver =  forms.TypedChoiceField(
		label="Type",
		choices=[
			('payment', 'Payment'),
			('charge', 'Charge')
		],
		coerce=lambda o: o == 'charge',
		widget=forms.RadioSelect(),
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


class TransactionListForm(forms.Form):
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
		required=False
	)
	transaction_type = forms.ChoiceField(
		choices=[
			('', 'All'),
			('payment', 'Payments'),
			('charge', 'Charges'),
		],
		required=False
	)
	status = forms.ChoiceField(
		choices=[
			('', 'All'),
			('pending', 'Pending'),
			('confirmed', 'Confirmed')
		],
		required=False
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
