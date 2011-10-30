from django.shortcuts import redirect
from django.http import HttpResponse
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from openlets.core import db
from openlets.openletsweb import forms
from openlets.openletsweb import web


def index(request):
	return web.render_context(request, 'index.html', 'login_form')

@login_required
def home(request):
	context = {}

	# New Transaction form
	new_trans_form_data = request.POST if request.method == 'POST' else None
	context['new_transaction_form'] = forms.TransactionRecordForm(
		new_trans_form_data,
		initial={
			'currency': request.user.person.default_currency
		}
	)

	# Pending transaction records
	context['pending_trans_records'] = db.get_pending_trans_for_user(request.user)

	return web.render_context(request, 'home.html', context=context)

@login_required
def settings(request):
	return web.render_context(request, 'settings.html')

@login_required
@require_POST
def new_transaction(request):
	form = forms.TransactionRecordForm(request.POST)
	if form.is_valid():
		form.save(request.user)
		messages.success(request, 'Transaction record saved.')
		return redirect('home')
	return home(request)
