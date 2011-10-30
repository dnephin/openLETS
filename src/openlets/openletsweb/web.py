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


def render_context(request, template, context=None, type='html', *args):
	"""Render a tempate with a context.  args are lookedup
	in `context_processors` and added to the context.

	Supported types:
		- html
	"""
	context_processors = [context_processor[arg] for arg in args]
	context = context or {}

	context = RequestContext(request, context or {}, context_processors)
	return render_to_response(template, context_instance=context)
	

