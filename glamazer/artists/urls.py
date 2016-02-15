from django.conf.urls import patterns, url
from django.views.generic import TemplateView

from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns('',
    url(r'^how_it_works/', TemplateView.as_view(template_name="core/how_it_works_artists.html"), name='artists_HIW'),
    url(r'^change_password/(?P<email_token>.*)', 'glamazer.users.views.change_password', name='change_password'),
    url(r'^forgotten_password/', 'glamazer.users.views.forgotten_password', name='forgotten_password'),
    url(r'^sign_up/$', 'glamazer.artists.views.sign_up', name='artists_sign_up'),
    url(r'^sign_up/facebook$', 'glamazer.artists.views.facebook_registration', name='artists_sign_up_facebook'),
    url(r'^profile/$', 'glamazer.artists.views.profile', name='artists_profile'),
    url(r'^profile/(?P<artist_id>.*)/(?P<name>.*)$', 'glamazer.artists.views.profile', name='profile_artist'),
    url(r'^settings/profile$', 'glamazer.artists.views.edit', name='edit_artist_profile'),
    url(r'^settings/account$', 'glamazer.artists.views.account', name='edit_artist_account'),
    url(r'^settings/payments$', 'glamazer.artists.views.payments', name='artist_payments'),
    url(r'^settings/policy$', 'glamazer.artists.views.cancellation_policy', name='artist_cancellation_policy'),
    url(r'^management/listings$', 'glamazer.artists.views.all_listings', name='all_listing'),
    url(r'^management/schedule$', 'glamazer.artists.views.schedule', name='artist_schedule'),
    url(r'^management/calendar/$', 'glamazer.artists.views.calendar', name='artists_calendar'),
    url(r'^management/statistic/$', TemplateView.as_view(template_name="artists/management/stats.html"), name='artists_statistic'),
    url(r'^settings/widgets$', 'glamazer.widget.views.create_widget', name='artist_widgets'),
    url(r'^upload/$', 'glamazer.artists.views.upload', name='upload'),
    url(r'^bookings/$', 'glamazer.artists.views.bookings', name='artists_bookings'),
    url(r'^bookings/report$', 'glamazer.users.views.report_problem', name='artists_report_booking'),
    url(r'^wallet/$', 'glamazer.artists.views.wallet', name='artists_wallet'),
    url(r'^withdraw/$', 'glamazer.artists.views.withdraw', name='artists_withdraw'),
    url(r'^notifications/$', 'glamazer.notifications.views.show_notifications', name='artist_notifications'),
    url(r'^get_chart_info/$', 'glamazer.artists.views.get_chart_info', name='get_chart_info'),
    url(r'^salon_suspend/(?P<salon_id>.*)$', 'glamazer.artists.views.salon_suspend', name='salon_suspend'),
    url(r'^salon_apply/(?P<salon_id>.*)$', 'glamazer.artists.views.salon_apply', name='salon_apply'),
)
