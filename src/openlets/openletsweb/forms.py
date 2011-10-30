from django import forms
from openlets.core import models

# TODO: tests
class TransactionRecordForm(forms.ModelForm):
	"""A Form for creating new TransactionRecord objects."""

	class Meta:
		model = models.TransactionRecord
		fields = ('currency', 'transaction_time')

	person = forms.ModelChoiceField(models.Person.objects.all())
	from_provider =  forms.TypedChoiceField(
		label="Type",
		choices=[
			('payment', 'Payment'),
			('charge', 'Charge')
		],
		coerce=lambda o: o == 'payment',
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
		if data['from_provider']:
			trans_rec.provider = active_user.person
			trans_rec.receiver = data['person']
		else:
			trans_rec.provider = data['person']
			trans_rec.receiver = active_user.person

		if commit:
			return trans_rec.save()
		return trans_rec
			





		
