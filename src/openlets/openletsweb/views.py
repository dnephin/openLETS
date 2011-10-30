from django.http import HttpResponse

from openlets.core import db
from openlets.openletsweb import web


def index(request):
	return web.render_context(request, 'index.html', 'login_form')

def home(request):
	return web.render_context(request, 'home.html')

def settings(request):
	return web.render_context(request, 'settings.html')
