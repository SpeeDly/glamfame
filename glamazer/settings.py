"""
Django settings for glamazer project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from production_settings import *
from os.path import abspath, dirname, join

ugettext = lambda s: s
LANGUAGES = (
    ('en', ugettext('English')),
    ('bg', ugettext('Bulgarian')),
    ('ru', ugettext('Russian')),
)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
LOCALE_PATHS = (
    join(BASE_DIR, 'locale'),
)


HOURS = ['8:00 AM', '8:30 AM', '9:00 AM', '9:30 AM', '10:00 AM', '10:30 AM', '11:00 AM', '11:30 AM', '12:00 PM', '12:30 PM', '1:00 PM', '1:30 PM', '2:00 PM', '2:30 PM', '3:00 PM', '3:30 PM', '4:00 PM', '4:30 PM', '5:00 PM', '5:30 PM', '6:00 PM', '6:30 PM', '7:00 PM', '7:30 PM', '8:00 PM']
STYLE_INDEXES = ((0, 'Hair',), (1, 'Nails',), (2, 'Make up',))
DURATION = (('1800', '00:30',), ('3600', '1:00',), ('5400', '1:30',), ('7200', '2:00',), ('9000', '2:30',), ('10800', '3:00',), ('12600', '3:30',), ('14400', '4:00',))
STATUS = ((0, 'PENDING',), (1, 'APPROVED',), (2, 'REJECTED',), (3, 'PASSED',), (4, 'REPORTED',))
LISTING_STATUS = ((0, 'Pending',), (1, 'Active',), (2, 'Not active',), (3, 'Forbidden',))
CANCELLED_BY = ['Not cancelled', 'Cancelled by artist', 'Cancelled by user']
CURRENCY = (('USD', '$',), ('EUR', '€',), ('GBP', '£',), ('RUB', 'RUB',))
NOTIFICATIONS_SHORT = [
    ugettext('{name} sent you a booking request '),
    ugettext('{name} accepted your booking request. '),
    ugettext('{name} declined your booking request. '),
    ugettext('{name} cancelled your appointment. '),
    ugettext('{name} cancelled an appointment. '),
    ugettext('We just transferred $ {amount} to your bank account. '),
    ugettext('{name} started following you. '),
    ugettext('{name} added a listing of yours in wishlist. '),
    ugettext('{name} reviewed your listing. '),
    ugettext('{name} uploaded new listing.'),
    ugettext('Congrats! Your listing was approved.'),
    ugettext('Your listing was rejected. Try again.'),
    ugettext('{name} wants to join your team.'),
    ugettext('{name} wants to suspend his membership.'),
    ugettext('{name} approved your membership.'),
    ugettext('{name} declined your membership.'),
    ugettext('Your suspension request has been approved.'),
    ugettext('Your suspension request has been declined.'),
]

NOTIFICATIONS_LONG = [
    ugettext('<a href="/users/profile/{id}">{name}</a> sent you a booking request for <a href="/listings/{listing_id}">{title}</a>. Manage your booking requests from <a href="/artists/bookings">here</a> '),
    ugettext('<a href="/artists/profile/{id}">{name}</a> accepted your booking request for <a href="/listings/{listing_id}">{title}</a>. View all your appointments <a href="/users/bookings">here</a>. '),
    ugettext('<a href="/artists/profile/{id}">{name}</a> declined your booking request for <a href="/listings/{listing_id}">{title}</a>. Click <a href="/listings/{listing_id}">here</a> to schedule appointment for a different hour. '),
    ugettext('Bad news! <a href="/artists/profile/{id}">{name}</a> cancelled your appointment for <a href="/listings/{listing_id}">{title}</a>. Your money will be refunded in 24 hours. As a little compensation from our side, your next booking will be with 5% discount from the regular price.'),
    ugettext('We are sorry to inform you that <a href="/users/profile/{id}">{name}</a> cancelled the appointment for <a href="/listings/{listing_id}">{title}</a>. Please search again for alternative listings.'),
    ugettext('Hey, <a href="/artists/profile/{id}">{name}</a>! Good news! We just transferred $ {amount} to your bank account. View your wallet here. '),
    ugettext('<a href="/{type}/profile/{id}">{name}</a> started following you. View all your followers <a href="/artists/profile">here</a>. '),
    ugettext('<a href="/{type}/profile/{id}">{name}</a> added a listing of yours in wishlist – <a href="/listings/{listing_id}">{title}</a>. '),
    ugettext('<a href="/users/profile/{id}">{name}</a> reviewed your listing – <a href="/listings/{listing_id}">{title}</a>. '),
    ugettext('<a href="/artists/profile/{id}">{name}</a> uploaded new listing – <a href="/listings/{listing_id}">{title}</a>. Click <a href="/listings/{listing_id}">here</a> to check the listing. '),
    ugettext('Congrats! Your <a href="/listings/{listing_id}">listing</a> was approved. You can edit it from the <a href="/{type}/listings">"Listings"</a> section of your profile. Observe the bookings for each listing, accept, or cancel them from the <a href="/{type}/bookings">"Bookings"</a> section of your profile.'),
    ugettext('We are sorry. Your <a href="/listings/{listing_id}">listing</a> has been rejected. The reason for that may be: duplicate content, irrelevant description of the listing; or wrong price, title and tag. Review the listing, correct your data and try again.'),
    ugettext('{name} wants to join your team.'),
    ugettext('{name} wants to suspend his membership.'),
    ugettext('{name} approved your membership.'),
    ugettext('{name} declined your membership.'),
    ugettext('Your suspension request has been approved.'),
    ugettext('Your suspension request has been declined.'),
]

#SMS texts
SMS = [
    ugettext('{name} sent you a booking request, check your bookings page. Confirm or reject it.'),
    ugettext('{name} accepted your booking request. Review your bookings: http://www.glamfame.com/users/bookings'),
    ugettext('{name} declined your booking request. Look up for alternative listings: http://www.glamfame.com/'),
    ugettext('{name} cancelled your appointment. You will receive 100% refund.'),
    ugettext('{name} cancelled an appointment.You will receive compensation according to your cancellation policy '),
    ugettext('We just transferred $ {amount} to your bank account. '),
    ugettext('We just transferred $ {amount} as refund to your bank account'),
]


SUBJECTS = [
    ugettext('Welcome to Glamfame!'),
    ugettext('Forgotten Password!'),
    ugettext('Hey. {username}, we miss you!'),
    ugettext('Hey. {username}, we miss you even more!'),
    ugettext('Don’t forget us!'),
    ugettext('{username} started following you!'),
    ugettext('{username} started following {artistname}!'),
    ugettext('Booking request for {title}'),
    ugettext('{username} started following you!'),
    ugettext('Your booking request has been approved!'),
    ugettext('Your booking request has been declined!'),
    ugettext('Appointment for {when} has been cancelled!'),
    ugettext('We hope your appointment went well '),
    ugettext('{username} posted a review of {title}'),
    ugettext('{amaunt} was transferred to your bank account '),
    ugettext('Welcome to Glamfame! {salon_name} added you as a member of its team.')
]

SENDER = 'team@glamfame.com'
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# Min Withdraw
MIN_WITHDRAW = 30

SECRET_KEY = '@0enryuhp0r0_b-5i&u4&huer-k%)j+jo4!8-0j#j_k$wozhs+'

FACEBOOK_APP_ID = '771259596233505'
FACEBOOK_API_SECRET = '6bd5ee707c3e4ff4c29a44c97235b5d2'

# Mandrill information
# Email: admin@glamfame.com
# Password: fame123123
MANDRILL_API_KEY = "WWTO6lZktIVqSyABnYwQNQ"

# PAYMILL Private test key and Public test key
# Email: payments@glamfame.com
# Password: fame123123
PR_PAYMILL_API_KEY = "2430d1c36a2be8a1bdf73826aea9f8f1"
PU_PAYMILL_API_KEY = "194148900473074936e072eb0a0f8de0"

# Twilio logins
# Email: zhuhov@gmail.com
# Password: 9210224526
ACCOUNT_SID = "AC148f9b9596f061e2f630f3acc5564ec1"
AUTH_TOKEN = "c92db1831368edd85df9561ab22d333b"
TWILIO_NUMBER = "+12135169309"
# PAYPAL ID
# Email: paypal@itworks.bg
# Password: ivoivo123
PAYPAL_API_KEY = "6S8D3DVM79PFN"
PAYPAL_MODE = 'sandbox'
PAYPAL_CLIENT_ID = 'AcmSsxAA8yEt9omPyFby9U9UNIVVqrEbW6x2tLjTQMbHvu8k1jNyMFtpBqwK'
PAYPAL_CLIENT_SECRET = 'EBaSVhBddvSz62BFwcG95-6mAaRELgNNIdA4-1Zty2DuMtOadM8eqkJ_Kj-8'

# Payment methods
PAYMENTS_METHOD = ['Bank Transfer', 'PayPal', 'Paymill']

# Withdraw status
WITHDRAW_STATUS = ((0, 'Pending',), (1, 'Accepted',), (2, 'Rejected',), (3, 'Warning',))


ALLOWED_HOSTS = ['glamfame.com', 'm.glamfame.com', 'www.glamfame.com', 'localhost', '127.0.0.1', '172.25.0.150']

PROJECT_ROOT = abspath(dirname(dirname(__file__)))

TEMPLATE_URL = join(PROJECT_ROOT, 'templates/')

DESKTOP_TEMPLATE_DIRS = (
    PROJECT_ROOT + '/templates',
)

MOBILE_TEMPLATE_DIRS = (
    PROJECT_ROOT + '/mobile_templates',
) + DESKTOP_TEMPLATE_DIRS

TEMPLATE_DIRS = DESKTOP_TEMPLATE_DIRS


CRON_CLASSES = [
    "glamazer.core.cron.SendFeedbackForm",
]

# Application definition
INSTALLED_APPS = (
    'suit',
    'django_cron',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'sorl.thumbnail',
    'glamazer.core',
    'glamazer.users',
    'glamazer.artists',
    'glamazer.salons',
    'glamazer.listings',
    'glamazer.followers',
    'glamazer.favorites',
    'glamazer.booking',
    'glamazer.notifications',
    'glamazer.payments',
    'glamazer.reviews',
    'glamazer.widget',
    'django_extensions',
    'south',
    'haystack',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'glamazer.core.middleware.MobileMiddleware',
    'glamazer.core.middleware.LangMiddleware'
)

DEBUG_TOOLBAR_PANELS = [
    'debug_toolbar.panels.versions.VersionsPanel',
    'debug_toolbar.panels.timer.TimerPanel',
    'debug_toolbar.panels.settings.SettingsPanel',
    'debug_toolbar.panels.headers.HeadersPanel',
    'debug_toolbar.panels.request.RequestPanel',
    'debug_toolbar.panels.sql.SQLPanel',
    'debug_toolbar.panels.staticfiles.StaticFilesPanel',
    'debug_toolbar.panels.templates.TemplatesPanel',
    'debug_toolbar.panels.cache.CachePanel',
    'debug_toolbar.panels.signals.SignalsPanel',
    'debug_toolbar.panels.logging.LoggingPanel',
    'debug_toolbar.panels.redirects.RedirectsPanel',
    'haystack_panel.panel.HaystackDebugPanel',
    'template_timings_panel.panels.TemplateTimings.TemplateTimings',
]

if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
    print(os.path.join(BASE_DIR, 'db.sqlite3'))
    INSTALLED_APPS += ('debug_toolbar', 'haystack_panel', 'template_timings_panel',)
    INSTALLED_APPS += ('raven.contrib.django.raven_compat',)

    MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)

else:
    DATABASES = {
        'default': {
            'NAME': 'glamazer',
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'HOST': '127.0.0.1',
            'PORT': '5432',
            'USER': 'glamfame',
            'PASSWORD': 'glam123',
        }
    }

    INSTALLED_APPS += ('raven.contrib.django.raven_compat',)
    # GetSentry configuration
    # Email: zhuhov@gmail.com
    # Pass: 9210224526
    RAVEN_CONFIG = {
        'dsn': 'https://e30d054ce88645609304fa8c1af5d28d:1efcabc6ed6740389b6610bb61d0e084@app.getsentry.com/24706',
    }


ELASTIC_SEARCH_URL = 'http://127.0.0.1:9200/'

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://127.0.0.1:9200/',
        'INDEX_NAME': 'haystack',
    },
    'default_ru': {
        'ENGINE': 'haystack.backends.elasticsearch_backend.ElasticsearchSearchEngine',
        'URL': 'http://127.0.0.1:9201/',
        'INDEX_NAME': 'haystack2',
    },
}


HAYSTACK_SIGNAL_PROCESSOR = 'haystack.signals.RealtimeSignalProcessor'


TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
    ('django.template.loaders.cached.Loader', (
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    )),
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.tz',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
)

AUTHENTICATION_BACKENDS = (
    'backends.EmailAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
)

ROOT_URLCONF = 'glamazer.urls'

WSGI_APPLICATION = 'glamazer.wsgi.application'

CONN_MAX_AGE = 60


# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

# LANGUAGE_CODE = 'en-us'
LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = False

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/


STATIC_ROOT = os.path.abspath(PROJECT_ROOT+'/static_server')
STATIC_URL = '/static/'


MEDIA_URL = '/media/'
MEDIA_FOLDER = 'media'
MEDIA_ROOT = join(PROJECT_ROOT, MEDIA_FOLDER + '/')


STATICFILES_DIRS = (join(PROJECT_ROOT,'static/'), )

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

EMAIL_BACKEND = "djrill.mail.backends.djrill.DjrillBackend"

EMAIL_CASES = {
    0: ugettext('User welcome message'),
    1: ugettext('Artist welcome message'),
    2: ugettext('Salon welcome message'),
    3: ugettext('Facebook welcome message'),
    4: ugettext('Forgotten password message'),
    5: ugettext('If not logged in after 3 days'),
    6: ugettext('If not logged in after 7 days'),
    7: ugettext('If not logged in after 14 days'),
    8: ugettext('Email to artist, in case of new follower'),
    9: ugettext('Email to artist, in case of new follower, in case he is assigned to salon'),
    10: ugettext('Email artist when he have new booking request'),
    11: ugettext('10, if he is assigned to salon'),
    12: ugettext('Email to the user, if the booking is approved'),
    13: ugettext('If booking request is rejected by artist'),
    14: ugettext('If booking request is declined by user, no charge'),
    15: ugettext('If booking request is declined by user, with charge'),
    16: ugettext('If booking request is cancelled by the artist, after was approved'),
    17: ugettext('User welcome message'),
    18: ugettext('User welcome message'),
}


SUIT_CONFIG = {
    'ADMIN_NAME': 'Glamfame',
    # 'HEADER_DATE_FORMAT': 'l, j. F Y',
    # 'HEADER_TIME_FORMAT': 'H:i',

    # menu
    # 'SEARCH_URL': '/admin/auth/user/',
    # 'MENU_ICONS': {
    #    'sites': 'icon-leaf',
    #    'auth': 'icon-lock',
    # },
    # 'MENU_OPEN_FIRST_CHILD': True, # Default True
    # 'MENU_EXCLUDE': ('auth.group',),
    # 'MENU': (
    #     'sites',
    #     {'app': 'auth', 'icon':'icon-lock', 'models': ('user', 'group')},
    #     {'label': 'Settings', 'icon':'icon-cog', 'models': ('auth.user', 'auth.group')},
    #     {'label': 'Support', 'icon':'icon-question-sign', 'url': '/support/'},
    # ),

    # misc
    # 'LIST_PER_PAGE': 15
}

DATE_FORMAT = 'Y-m-d'
DATETIME_FORMAT = 'Y-m-d H:i:s'
