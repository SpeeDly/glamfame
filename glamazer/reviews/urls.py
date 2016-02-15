from django.conf.urls import patterns, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^(?P<email_token>.*)$', 'glamazer.reviews.views.receive_review', name='receive_review'),
)
