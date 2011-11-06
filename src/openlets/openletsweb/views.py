from django.shortcuts import redirect
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from django.contrib.auth import forms as auth_forms
from django.contrib import messages

from openlets.core import db
from openlets.openletsweb import forms
from openlets.openletsweb import web


def index(request):
	return web.render_context(request, 'index.html', 'login_form')

@login_required
def home(request):
	"""Setup homepage context."""
	context = {}

	# New Transaction form
	new_trans_form_data = request.POST if request.method == 'POST' else None
	context['new_transaction_form'] = forms.TransactionRecordForm(
		web.form_data(request),
		initial={
			'currency': request.user.person.default_currency
		}
	)

	# TODO: link to any records for the user that may be for the same transaction
	# Pending transaction records
	context['pending_trans_records'] = db.get_pending_trans_for_user(request.user)

	# Recent transactions, that may be confirmed
	context['recent_trans_records'] = db.get_recent_trans_for_user(request.user)

	# Currency balances
	context['balances'] = db.get_balances(request.user)

	# TODO: notifications for recent changes
	context['notifications'] = None

	return web.render_context(request, 'home.html', context=context)

@login_required
def settings(request):
	"""Build context for settings page."""
	context = {}
	# TODO:usage statistics

	# User account form
	context['user_form'] = forms.UserForm(
		web.form_data(request),
		instance=request.user
	)
	context['password_form'] = auth_forms.PasswordChangeForm(
		web.form_data(request)
	)

	# Person forms
	context['person_form'] = forms.PersonForm(
		web.form_data(request),
		instance=request.user.person
	)

	# Exchange rates
	context['exchange_rates'] = db.get_exchange_rates(request.user)
	context['exchange_rate_form'] = forms.ExchangeRateForm(
		web.form_data(request)
	)
	return web.render_context(request, 'settings.html', context=context)

@login_required
@require_POST
def exchange_rate_new(request):
	form = forms.ExchangeRateForm(request.POST)
	if form.is_valid():
		form.save(request.user)
		messages.success(request, 'Exchange rate created.')
		return redirect('settings')
	return settings(request)

@login_required
@require_POST
def person_update(request):
	"""Update person details."""
	form = forms.PersonForm(request.POST, instance=request.user.person)
	if form.is_valid():
		form.save()
		messages.success(request, 'Settings updated.')
		return redirect('settings')
	return settings(request)

@login_required
@require_POST
def user_update(request):
	form = forms.UserForm(request.POST, instance=request.user)
	if form.is_valid():
		form.save()
		messages.success(request, 'Account updated.')
		return redirect('settings')
	return settings(request)

@login_required
@require_POST
def transaction_new(request):
	"""Create a new transaction record."""
	form = forms.TransactionRecordForm(request.POST)
	if form.is_valid():
		form.save(request.user)
		messages.success(request, 'Transaction record saved.')
		return redirect('home')
	return home(request)

@require_GET
def transaction_list(request):
	"""List transactions."""
	context = {}
	context['filter_form'] = filter_form = forms.TransferListForm(request.GET)
	filters = filter_form.cleaned_data if filter_form.is_valid() else {}

	context['records'] = db.get_transfer_history(request.user, filters)
	return web.render_context(request, 'transaction_list.html', context=context)

@require_GET
def transaction_confirm(request, trans_record_id):
	"""Confirm a transaction record from another person."""
	trans_record = db.get_trans_record_for_user(trans_record_id, request.user)
	db.confirm_trans_record(trans_record)
	messages.success(request, 'Transaction confirmed.')
	return redirect('home')

@require_GET
def transaction_modify(request, trans_record_id):
	"""Modify a transaction record from another person."""

