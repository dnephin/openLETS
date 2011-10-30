from django.shortcuts import redirect
from django.http import HttpResponse
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required

from openlets.core import db
from openlets.openletsweb import forms
from openlets.openletsweb import web


def index(request):
	return web.render_context(request, 'index.html', 'login_form')

@login_required
def home(request):
	context = {}
	context['new_transaction_form'] = forms.TransactionRecordForm(
		initial={
			'currency': request.user.person.default_currency
		}
	)
	return web.render_context(request, 'home.html', context=context)

@login_required
def settings(request):
	return web.render_context(request, 'settings.html')

@login_required
@require_POST
def new_transaction(request):
	form = forms.TransactionRecordForm(request.POST)
	if form.is_valid():
		form.save()
		return redirect('home')
	return home(request)
