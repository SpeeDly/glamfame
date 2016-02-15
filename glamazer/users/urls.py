from django.conf.urls import patterns, url
from django.views.generic import TemplateView

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^how_it_works/', TemplateView.as_view(template_name="core/how_it_works_users.html"), name='profiles_HIW'),
    url(r'^confirmation/(?P<email_token>.*)$', 'glamazer.users.views.confirmation', name='confirmation'),
    url(r'^change_password/(?P<email_token>.*)$', 'glamazer.users.views.change_password', name='change_password'),
    url(r'^forgotten_password/', 'glamazer.users.views.forgotten_password', name='forgotten_password'),
    url(r'^login/$', 'glamazer.users.views.login', name='login'),
    url(r'^sign_up/$', 'glamazer.users.views.sign_up', name='sign_up'),
    url(r'^logout/$', 'glamazer.users.views.logout_user', name='logout'),
    url(r'^wishlist/$', 'glamazer.users.views.wishlist', name='wishlist'),
    url(r'^followed/$', 'glamazer.users.views.followed', name='followed'),
    url(r'^change_email/$', 'glamazer.users.views.change_email', name='change_email'),
    url(r'^change_password_user/$', 'glamazer.users.views.change_password_user', name='change_password_user'),
    url(r'^sign_up/facebook', 'glamazer.users.views.facebook_registration', name='facebook_sign_up'),
    url(r'^login/facebook', 'glamazer.users.views.facebook_login', name='facebook_login'),
    url(r'^profile/$', 'glamazer.users.views.profile', name='user_profile'),
    url(r'^profile/(?P<user_id>.*)/(?P<name>.*)$', 'glamazer.users.views.profile', name='profile_user'),
    url(r'^settings', 'glamazer.users.views.settings', name='user_settings'),
    url(r'^bookings$', 'glamazer.users.views.bookings', name='profiles_bookings'),
    url(r'^bookings/report', 'glamazer.users.views.report_problem', name='profiles_report_booking'),
    url(r'^cancel', 'glamazer.users.views.cancel', name='booking_cancel'),
    url(r'^notifications/$', 'glamazer.notifications.views.show_notifications', name='user_notifications'),
)
