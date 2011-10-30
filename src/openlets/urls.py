from django.conf.urls.defaults import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^accounts/', include('django.contrib.auth.urls')),

    url(r'^$', 'openletsweb.views.index', name='index'),
    url(r'^home$', 'openletsweb.views.home', name='home'),
    url(r'^settings$', 'openletsweb.views.settings', name='settings'),

    url(r'^new_transaction$', 'openletsweb.views.new_transaction', name='new_transaction'),


    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
)
