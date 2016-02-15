from django.conf.urls import patterns, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^confirm/', 'glamazer.listings.views.confirm', name='booking_confirm'),
    url(r'^check_availability/$', 'glamazer.listings.views.check_availability', name='check_availability'),
    url(r'^edit/(?P<listing_id>.*)$', 'glamazer.listings.views.edit', name='edit_listing'),
    url(r'^delete/(?P<listing_id>.*)$', 'glamazer.listings.views.delete', name='delete_listing'),
    url(r'^activate/(?P<listing_id>.*)$', 'glamazer.listings.views.activate', name='activate_listing'),
    url(r'^(?P<listing_id>.*)/(?P<title>.*)$', 'glamazer.listings.views.show', name='listing'),
)
