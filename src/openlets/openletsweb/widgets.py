"""
 Custom form widgets
"""
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe
from django.utils.encoding import StrAndUnicode, force_unicode
from django.forms import widgets as core_widgets


class RadioButton(core_widgets.RadioInput):
	"""Render a single input type="radio"."""

	def __unicode__(self):
		"""Largely taken from parent class."""
		choice_label = conditional_escape(force_unicode(self.choice_label))
		return mark_safe(
			u'%s<span> %s</span>' % (self.tag(), choice_label)
		)


class UnstyledRadioRenderer(core_widgets.RadioFieldRenderer):
	"""A radio button render for JQuery ui radio buttons."""

	def __iter__(self):
		for i, choice in enumerate(self.choices):
			yield RadioButton(self.name, self.value, self.attrs.copy(), choice, i)

	def render(self):
		return mark_safe(
			u'<ul class="unstyled">\n%s\n</ul>' % (
				u'\n'.join(u'%s' % force_unicode(w) for w in self)
			)
		)

