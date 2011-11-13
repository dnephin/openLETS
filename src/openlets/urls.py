from django.conf.urls.defaults import patterns, include, url

from django.contrib import admin
admin.autodiscover()

from openletsweb import forms

auth_urlpatterns = patterns('django.contrib.auth.views',
    (r'^accounts/login/$', 'login', {'authentication_form': forms.LoginForm} ),
    (r'^accounts/logout/$', 'logout', {'next_page': '/'}),
    (r'^accounts/password_change/$', 'password_change', {'post_change_redirect': '/settings'}),
    (r'^accounts/password_reset/$', 'password_reset', {}, 'password_reset'),
    (r'^accounts/password_reset/done/$', 'password_reset_done'),
    (r'^accounts/reset/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', 'password_reset_confirm'),
    (r'^accounts/reset/done/$', 'password_reset_complete'),
)

web_urlpatterns = patterns('openletsweb.views',
    url(r'^$', 'index', name='index'),
    url(r'^home$', 'home', name='home'),
    url(r'^settings$', 'settings', name='settings'),

    url(r'^transaction/new$', 'transaction_new', name='transaction_new'),
    url(r'^transaction/list$', 'transaction_list', name='transaction_list'),
    url(r'^transaction/confirm/(\d+)$', 'transaction_confirm', name='transaction_confirm'),
    url(r'^transaction/modify/(\d+)$', 'transaction_modify', name='transaction_modify'),

    url(r'^settings/user/update$', 'user_update', name='user_update'),
    url(r'^settings/user/new$', 'user_new', name='user_new'),
    url(r'^settings/person/update$', 'person_update', name='person_update'),
    url(r'^exchange_rate/new$', 'exchange_rate_new', name='exchange_rate_new'),

    url(r'^export_data$', 'export_data', name='export_data'),

	url(r'^about$', 'content_view', {'name': 'about'}, 'about'),
	url(r'^contact$', 'content_view', {'name': 'contact'}, 'contact'),
)

admin_urlpatterns = patterns('',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)

urlpatterns = auth_urlpatterns + web_urlpatterns + admin_urlpatterns
