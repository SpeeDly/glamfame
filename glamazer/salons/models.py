import requests
import os

from django.db import models
from django.contrib.auth.models import User
from glamazer.notifications.models import Notification
from glamazer.settings import MEDIA_ROOT, STATIC_ROOT, CURRENCY


class Salon(models.Model):
    facebook_id = models.CharField(max_length=20, blank=True, null=True)
    user = models.OneToOneField(User, unique=True)
    lng = models.FloatField(default=0)
    lat = models.FloatField(default=0)
    description = models.TextField(null=True)
    avatar = models.CharField(max_length=128, blank=True, null=True)
    mobile_number = models.CharField(max_length=128, blank=True, null=True)
    money = models.FloatField(default=0)
    currency = models.CharField(max_length=128, choices=CURRENCY, default='USD')
    rating = models.FloatField(default=5)
    is_activated = models.BooleanField(default=False)
    step = models.IntegerField(default=0)
    enable_emails = models.BooleanField(default=True)
    enable_sms = models.BooleanField(default=False)

    def get_avatar(self):
        try:
            return MEDIA_ROOT + self.avatar[7:]
        except:
            return ''

    def get_name(self):
        return self.user.first_name

    def have_artist(self):
        from glamazer.artists.models import Artist
        if Artist.objects.filter(salon=self, is_activated=True).count():
            return True
        else:
            return False

    def get_address(self):
        url = 'http://maps.googleapis.com/maps/api/geocode/json?latlng={0},{1}&sensor=false'.format(self.lat, self.lng)
        request = requests.get(url)
        json_results = request.json()
        try:
            address = json_results['results'][6]['formatted_address']
        except:
            address = 'undefined'
        return address

    def get_all_images(self):
        ''' Try to get all pictures for the salon, if the folder is empty, return '''

        gallery = '{0}salons/{1}/gallery'.format(MEDIA_ROOT, self.id)
        if os.path.isdir(gallery):
            pictures = {}
            for f in os.listdir(gallery):
                pictures[f] = '{0}/{1}'.format(gallery, f)
        else:
            pictures = []
        return pictures

    def get_notification_count(self):
        '''get only the notifications count, whithout evaluate the query'''
        from glamazer.artists.models import Artist
        users = []
        artists = Artist.objects.select_related('user').filter(salon=self)
        for artist in artists:
            users.append(artist.user)

        users.append(self.user)

        notification_count = Notification.objects.filter(receiver__in=users, is_readed=False).count()
        return notification_count

    def get_notifications(self, limit=0):
        '''get all notifications for current instance and make them readed'''
        from glamazer.artists.models import Artist
        users = []
        artists = Artist.objects.select_related('user').filter(salon=self)
        for artist in artists:
            users.append(artist.user)

        users.append(self.user)

        if limit:
            notifications = Notification.objects.filter(receiver__in=users)[:limit]
        else:
            notifications = Notification.objects.filter(receiver__in=users)
        return notifications

    def __str__(self):
        return self.user.first_name

    def get_avatar_tag(self):
        try:
            return '<img src="%s" style="border-radius: 999px" />' % self.avatar
        except:
            return '<img src="%s" style="border-radius: 999px" />' % (STATIC_ROOT+'/img/default.png')

    def get_step(self):
        if not self.step:
            return 'Finished'
        else:
            return self.step

    def get_cancellation_rate(self):
        from glamazer.artists.models import Artist
        artists = Artist.objects.filter(salon=self)
        temp_rate = 0
        for a in artists:
            temp_rate += a.get_cancellation_rate()
        rate = temp_rate/len(artists)
        return rate

    get_avatar_tag.short_description = 'Avatar'
    get_avatar_tag.allow_tags = True

    get_name.allow_tags = True
    get_name.short_description = "Name"

    get_step.allow_tags = True
    get_step.short_description = "Step"
