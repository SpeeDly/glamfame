from django.conf.urls import patterns, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^add_new/(?P<listing_id>.*)', 'glamazer.favorites.views.add', name='add_favorite'),
)
