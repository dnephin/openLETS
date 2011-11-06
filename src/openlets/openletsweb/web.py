"""
Helpers, decorators and util functions for views.
"""

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.auth import forms

def login_form_processor(request):
	"""Add 'login_form' to the context if the user is not logged in."""
	if request.user.is_authenticated():
		return {}
	return {'login_form': forms.AuthenticationForm()}


context_processors = {
	'login_form':	login_form_processor
}


def render_context(request, template, context=None, type='html', processors=()):
	"""Render a tempate with a context.  args are lookedup
	in `context_processors` and added to the context.

	Supported types:
		- html
	"""
	use_processors = [context_processors[arg] for arg in processors]
	context = context or {}

	context = RequestContext(request, context or {}, use_processors)
	return render_to_response(template, context_instance=context)
	

def form_data(request, expected='POST'):
	"""Get the expected form data if the request method matches expected,
	otherwise return None.  Used to get form data.
	"""
	return getattr(request, expected) if request.method == expected else None
