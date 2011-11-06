from django.conf.urls.defaults import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^accounts/', include('django.contrib.auth.urls')),

    url(r'^$', 'openletsweb.views.index', name='index'),
    url(r'^home$', 'openletsweb.views.home', name='home'),
    url(r'^settings$', 'openletsweb.views.settings', name='settings'),

    url(r'^transaction/new$', 'openletsweb.views.transaction_new', name='transaction_new'),
    url(r'^transaction/list$', 'openletsweb.views.transaction_list', name='transaction_list'),

    url(r'^transaction/confirm/(\d+)$', 
		'openletsweb.views.transaction_confirm', 
		name='transaction_confirm'),
    url(r'^transaction/modify/(\d+)$', 
		'openletsweb.views.transaction_modify', 
		name='transaction_modify'),

    url(r'^settings/user/update$',
		'openletsweb.views.user_update',
		name='user_update'),
    url(r'^settings/person/update$',
		'openletsweb.views.person_update',
		name='person_update'),
    url(r'^exchange_rate/new$', 
		'openletsweb.views.exchange_rate_new', 
		name='exchange_rate_new'),


    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
