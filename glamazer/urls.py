from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

admin.autodiscover()


urlpatterns = patterns('',
    url(r'^$', 'glamazer.core.views.home', name='home'),
    url(r'^hairstyle/', 'glamazer.core.views.base', name='hair'),
    url(r'^nails-design/', 'glamazer.core.views.base', name='nails'),
    url(r'^make-up/', 'glamazer.core.views.base', name='make_up'),
    url(r'^style/', 'glamazer.core.views.base', name='style'),
    url(r'^contest/', 'glamazer.core.views.base', name='contest'),
    url(r'^leaderboards/', 'glamazer.core.views.base', name='leaderboards'),
    url(r'^result/', 'glamazer.core.views.search', name='result'),
    url(r'^get_notifications/', 'glamazer.notifications.views.get_notifications', name='short_notifications'),
    url(r'^get_notifications_count/', 'glamazer.notifications.views.get_notification_count', name='notification_count'),
    url(r'^autocomplete_tags/', 'glamazer.core.views.autocomplete_tags', name='autocomplete_tags'),
    url(r'^sign_up/', TemplateView.as_view(template_name="sign_up.html"), name='signup'),
    url(r'^terms/', TemplateView.as_view(template_name="core/terms.html"), name='terms'),
    url(r'^imprint/', TemplateView.as_view(template_name="core/imprint.html"), name='imprint'),
    url(r'^privacy/', TemplateView.as_view(template_name="core/privacy.html"), name='privacy'),
    url(r'^faq/', TemplateView.as_view(template_name="core/faq.html"), name='faq'),
    url(r'^about_us/', TemplateView.as_view(template_name="core/about_us.html"), name='about_us'),
    url(r'^contacts/', TemplateView.as_view(template_name="core/contact_us.html"), name='contacts'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^users/', include('glamazer.users.urls')),
    url(r'^artists/', include('glamazer.artists.urls')),
    url(r'^salons/', include('glamazer.salons.urls')),
    url(r'^listings/', include('glamazer.listings.urls')),
    url(r'^favorites/', include('glamazer.favorites.urls')),
    url(r'^reviews/', include('glamazer.reviews.urls')),
    url(r'^widget/', include('glamazer.widget.urls')),
    url(r'^success/', 'glamazer.payments.views.success_payment', name='success'),
    url(r'^error/', 'glamazer.payments.views.error_payment', name='error'),
    url(r'^cancel/', 'glamazer.payments.views.cancel_payment', name='cancel'),
    url(r'^get_hint/', 'glamazer.core.views.get_hint', name='get_hint'),
    url(r'^start_payment/', 'glamazer.payments.views.start_payment', name='paypal_payment'),
    url(r'^send_feedback/$', 'glamazer.users.views.send_feedback', name='send_feedback'),
)

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
