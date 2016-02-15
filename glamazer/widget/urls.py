from django.conf.urls import patterns, url
from django.contrib import admin

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^(?P<token>.*)', 'glamazer.widget.views.widget', name='generate_widget'),
)
