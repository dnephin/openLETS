import datetime
from django.shortcuts import redirect
from django.views.decorators.http import require_POST, require_GET
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings as config

from openlets.core import db
from openlets.openletsweb import forms
from openlets.openletsweb import web
from openlets.openletsweb import models
from openlets.openletsweb.util import trans_matcher 


def index(request):
	if request.user.is_authenticated():
		return redirect('home')

	intro = models.Content.objects.get(name='intro', site=config.SITE_ID)
	context = {
		'login_form': forms.LoginForm(),
		'user_form': forms.UserCreateForm(web.form_data(request)),
		'intro': intro 
	}
	return web.render_context(request, 'index.html', context=context)



def build_pending_trans_records(request):
	"""Supplement the pending trans records with a modify form
	and attempt to link them to any trans_records created by the
	user.
	"""
	recent_pending = db.get_recent_trans_for_user(
		request.user, limit=100, pending_only=True)
	pending_trans_records = db.get_pending_trans_for_user(request.user)
	for trans_record in pending_trans_records:
		cur_user_trans_record = None
		if trans_record.transaction:
			cur_user_trans_record = trans_record.other_trans_record
		trans_record.modify_form = forms.TransactionRecordForm(
			instance=cur_user_trans_record
		)
		trans_record.approve_with_record = trans_matcher.find_similar(
			recent_pending, trans_record
		)
		yield trans_record

@login_required
def home(request):
	"""Setup homepage context."""
	context = {}

	# New Transaction form
	new_trans_form_data = request.POST if request.method == 'POST' else None
	context['new_transaction_form'] = forms.TransactionRecordForm(
		web.form_data(request),
		initial={
			'currency': request.user.person.default_currency,
			'transaction_time': datetime.datetime.now().strftime('%x %X')
		}
	)

	context['pending_trans_records'] = build_pending_trans_records(request)

	# Recent transactions, that may be confirmed
	context['recent_trans_records'] = db.get_recent_trans_for_user(request.user)

	# Currency balances
	context['balances'] = db.get_balances(request.user)

	# TODO: notifications for recent news, transactions, balances
	context['notifications'] = None

	return web.render_context(request, 'home.html', context=context)

@login_required
def settings(request):
	"""Build context for settings page."""
	context = {}
	# TODO:usage statistics

	# User account form
	context['user_form'] = forms.UserEditForm(
		web.form_data(request),
		instance=request.user
	)
	context['password_form'] = forms.PasswordChangeForm(
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
	form = forms.UserEditForm(request.POST, instance=request.user)
	if form.is_valid():
		form.save()
		messages.success(request, 'Account updated.')
		return redirect('settings')
	return settings(request)

@require_POST
def user_new(request):
	pass

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


def content_view(request, name):
	"""Get a piece of content by name."""
	content = models.Content.objects.get(name=name, site=config.SITE_ID)
	return web.render_context(request, 'content.html',
		context={'content': content}
	)
