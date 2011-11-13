"""
 Custom form widgets
"""
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.utils.encoding import StrAndUnicode, force_unicode
from django.forms import widgets as core_widgets
from django.forms.forms import pretty_name


class RadioButton(core_widgets.RadioInput):
	"""Render a single input type="radio"."""

	def __unicode__(self):
		"""Largely taken from parent class."""
		choice_label = conditional_escape(force_unicode(self.choice_label))
		return mark_safe(
			u'<li><label>%s<span> %s</span></label></li>' % (self.tag(), choice_label)
		)


class UnstyledRadioRenderer(core_widgets.RadioFieldRenderer):
	"""A radio button render for JQuery ui radio buttons."""

	def __iter__(self):
		for i, choice in enumerate(self.choices):
			yield RadioButton(self.name, self.value, self.attrs.copy(), choice, i)

	def render(self):
		return mark_safe(
			u'<ul class="inputs-list">\n%s\n</ul>' % (
				u'\n'.join(u'%s' % force_unicode(w) for w in self)
			)
		)

class PlaceholderTextInput(core_widgets.TextInput):
	"""A text input that uses placeholder for its label."""

	def render(self, name, value, attrs=None):
		attrs = attrs or {}
		# TODO: this overrides a label on a field, and shouldnt
		attrs['placeholder'] = pretty_name(name)
		return super(PlaceholderTextInput, self).render(name, value, attrs)

class PlaceholderPasswordInput(core_widgets.PasswordInput):

	def render(self, name, value, attrs=None):
		attrs = attrs or {}
		# TODO: this overrides a label on a field, and shouldnt
		attrs['placeholder'] = pretty_name(name)
		return super(PlaceholderPasswordInput, self).render(name, value, attrs)

