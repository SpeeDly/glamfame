from django.conf import settings
from django.utils import simplejson, translation
from glamazer.core.mobile_detection import UAgentInfo


class MobileMiddleware:
    def process_request(self, request):
        ''' Double check(nginx and python) for mobile/tablet/desktop. We can put this information in the request variable in the following way: request.is_mobile = is_mobile, request.is_tablet = is_tablet, request.is_phone = is_phone.'''
        subdomain = request.META.get('HTTP_X_FORWARDED_HOST', '').split('.')
        user_agent = request.META.get("HTTP_USER_AGENT")
        http_accept = request.META.get("HTTP_ACCEPT")
        is_tablet = False
        if user_agent and http_accept:
            agent = UAgentInfo(userAgent=user_agent, httpAccept=http_accept)
            is_tablet = agent.detectTierTablet()

        if settings.MOBILE_ONLY or ('m' in subdomain and not is_tablet):
            settings.TEMPLATE_DIRS = settings.MOBILE_TEMPLATE_DIRS
        else:
            settings.TEMPLATE_DIRS = settings.DESKTOP_TEMPLATE_DIRS


class LangMiddleware:
    def process_request(self, request):
        print(request.META.get('HTTP_X_FORWARDED_HOST', ''))
        try:
            lang = request.META['HTTP_X_FORWARDED_HOST'].split("glamfame.")[1].split("/")[0]
            if lang == "ru":
                lang = "ru"
                settings.DATABASES['default']['NAME'] = 'glamazerru'
                settings.ELASTIC_SEARCH_URL = 'http://127.0.0.1:9201/'
                settings.HAYSTACK_CONNECTIONS["default"]["URL"] = settings.ELASTIC_SEARCH_URL
                settings.MEDIA_FOLDER = 'media_ru'
            elif lang == "com":
                lang = "en"
                settings.DATABASES['default']['NAME'] = 'glamazer'
                settings.ELASTIC_SEARCH_URL = 'http://127.0.0.1:9200/'
                settings.HAYSTACK_CONNECTIONS["default"]["URL"] = settings.ELASTIC_SEARCH_URL
                settings.MEDIA_FOLDER = 'media'

            request.session['django_language'] = lang
            translation.activate(lang)
        except:
            try:
                lang = request.META['HTTP_HOST'].split(":")[1].split("/")[0]
            except:
                lang = "8000"
            if lang == "8000":
                lang = "en"
                request.session['django_language'] = lang
                translation.activate(lang)
                settings.__LANG = "EN"
