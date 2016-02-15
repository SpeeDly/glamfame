import requests

from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from glamazer.salons.models import Salon
from glamazer.notifications.models import Notification
from glamazer.settings import MEDIA_ROOT, STYLE_INDEXES, HOURS, CURRENCY

POLICY_STATUS = ((0, 'Pending',), (1, 'Current',), (2, 'Was Approved',), (3, 'Rejected',))


class Artist(models.Model):
    facebook_id = models.CharField(max_length=20, blank=True, null=True)
    user = models.OneToOneField(User, unique=True)
    salon = models.ForeignKey(Salon, null=True, blank=True)
    lng = models.FloatField(default=0)
    lat = models.FloatField(default=0)
    description = models.TextField(null=True)
    currency = models.CharField(max_length=8, choices=CURRENCY, default='USD')
    avatar = models.CharField(max_length=128, blank=True, null=True)
    custom_fee = models.IntegerField(blank=True, null=True)
    mobile_number = models.CharField(max_length=128, blank=True, null=True)
    money = models.FloatField(default=0)
    style = models.IntegerField(default=0, choices=STYLE_INDEXES)
    rating = models.FloatField(default=5)
    is_activated = models.BooleanField(default=True)
    enable_emails = models.BooleanField(default=True)
    enable_sms = models.BooleanField(default=False)
    step = models.IntegerField(default=0)
    waiting_for_hired = models.BooleanField(default=False)  # if true => The artist waiting for salon approving
    waiting_for_fired = models.BooleanField(default=False)  # if false => The artist waiting for salon approving for suspend

    def get_avatar(self):
        try:
            return MEDIA_ROOT + self.avatar[7:]
        except:
            return ''

    def get_salon_avatar(self):
        try:
            return MEDIA_ROOT + self.salon.avatar[7:]
        except:
            return ''

    def get_name(self):
        return self.user.first_name

    def get_salon_name(self):
        try:
            return self.salon.user.first_name
        except:
            return None

    def get_style(self):
        return STYLE_INDEXES[self.style][1]

    def get_address(self):
        url = 'http://maps.googleapis.com/maps/api/geocode/json?latlng={0},{1}&sensor=false'.format(self.lat, self.lng)
        request = requests.get(url)
        json_results = request.json()
        try:
            address = json_results['results'][6]['formatted_address']
        except:
            address = 'undefined'
        return address

    def get_notification_count(self):
        '''get only the notifications count, whithout evaluate the query'''
        notification_count = Notification.objects.filter(receiver=self.user, is_readed=False).count()
        return notification_count

    def get_notifications(self, limit=0):
        '''get all notifications for current instance and make them readed'''
        if limit:
            notifications = Notification.objects.filter(receiver=self.user)[:limit]
        else:
            notifications = Notification.objects.filter(receiver=self.user)

        return notifications

    def get_avatar_tag(self):
        return '<img src="%s" style="border-radius: 999px" />' % self.avatar

    def get_step(self):
        if not self.step:
            return 'Finished'
        else:
            return self.step

    def get_cancellation_rate(self):
        cr = CancellationRate.objects.get(artist=self)
        try:
            rate = (cr.cancelled*100)/(cr.approved)
        except:
            rate = 0
        return rate

    def salon_link(self):
        url = "None"
        try:
            url = '<a href="%s">%s</a>' % (reverse(("admin:salons_salon_change"), args=(self.salon_id, )), self.salon.user.first_name)
        except:
            pass

        return url

    def save(self, force_insert=False, force_update=False, **kwargs):
        if not self.id:
            super(Artist, self).save(force_insert, force_update)
            ArtistPolicy.objects.create(artist=self, cancellation_policy_id=1, status=1)
            CancellationRate.objects.create(artist=self)
        else:
            super(Artist, self).save(force_insert, force_update)

    salon_link.allow_tags = True
    salon_link.short_description = "Salon"

    get_avatar_tag.short_description = 'Avatar'
    get_avatar_tag.allow_tags = True

    get_name.allow_tags = True
    get_name.short_description = "Name"

    get_step.allow_tags = True
    get_step.short_description = "Step"

    def __str__(self):
        return self.user.first_name


class Busy(models.Model):
    artist = models.ForeignKey(Artist)
    comment = models.CharField(max_length=255, blank=True, null=True)
    start_time = models.IntegerField(default=0)
    end_time = models.IntegerField(default=0)


class WorkTime(models.Model):
    artist = models.ForeignKey(Artist)
    mon_start = models.IntegerField(blank=True, null=True, default="0")
    mon_end = models.IntegerField(blank=True, null=True, default="24")
    tues_start = models.IntegerField(blank=True, null=True, default="0")
    tues_end = models.IntegerField(blank=True, null=True, default="24")
    wed_start = models.IntegerField(blank=True, null=True, default="0")
    wed_end = models.IntegerField(blank=True, null=True, default="24")
    thurs_start = models.IntegerField(blank=True, null=True, default="0")
    thurs_end = models.IntegerField(blank=True, null=True, default="24")
    fri_start = models.IntegerField(blank=True, null=True, default="0")
    fri_end = models.IntegerField(blank=True, null=True, default="24")
    sat_start = models.IntegerField(blank=True, null=True, default="-1")
    sat_end = models.IntegerField(blank=True, null=True, default="-1")
    sun_start = models.IntegerField(blank=True, null=True, default="-1")
    sun_end = models.IntegerField(blank=True, null=True, default="-1")

    def get_serialiazed(self):
        return [[self.mon_start, self.mon_end],
                [self.tues_start, self.tues_end],
                [self.wed_start, self.wed_end],
                [self.thurs_start, self.thurs_end],
                [self.fri_start, self.fri_end],
                [self.sat_start, self.sat_end],
                [self.sun_start, self.sun_end]]

    def monday(self):
        if self.mon_start == -1:
            return _("Not working!")
        else:
            return '{0}-{1}'.format(HOURS[self.mon_start], HOURS[self.mon_end])

    def tuesday(self):
        if self.tues_start == -1:
            return _("Not working!")
        else:
            return '{0}-{1}'.format(HOURS[self.tues_start], HOURS[self.tues_end])

    def wednesday(self):
        if self.wed_start == -1:
            return _("Not working!")
        else:
            return '{0}-{1}'.format(HOURS[self.wed_start], HOURS[self.wed_end])

    def thursday(self):
        if self.thurs_start == -1:
            return _("Not working!")
        else:
            return '{0}-{1}'.format(HOURS[self.thurs_start], HOURS[self.thurs_end])

    def friday(self):
        if self.fri_start == -1:
            return _("Not working!")
        else:
            return '{0}-{1}'.format(HOURS[self.fri_start], HOURS[self.fri_end])

    def saturday(self):
        if self.sat_start == -1:
            return _("Not working!")
        else:
            return '{0}-{1}'.format(HOURS[self.sat_start], HOURS[self.sat_end])

    def sunday(self):
        if self.sun_start == -1:
            return _("Not working!")
        else:
            return '{0}-{1}'.format(HOURS[self.sun_start], HOURS[self.sun_end])


class CancellationRate(models.Model):
    artist = models.ForeignKey(Artist)
    cancelled = models.IntegerField(default=0)
    approved = models.IntegerField(default=0)


class CancellationPolicy(models.Model):
    cancellation_type = models.CharField(max_length=128, default="Custom")
    days_before = models.IntegerField()
    percent = models.IntegerField()
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.cancellation_type


class ArtistPolicy(models.Model):
    artist = models.ForeignKey(Artist)
    cancellation_policy = models.ForeignKey(CancellationPolicy)
    last_change = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(default=0, choices=POLICY_STATUS)

    def artist_link(self):
        url = '<a href="%s">%s</a>' % (reverse(("admin:artists_artist_change"), args=(self.artist_id, )), self.artist.user.first_name)
        return url

    def cancellation_policy_link(self):
        url = '<a href="%s">%s</a>' % (
            reverse(("admin:artists_cancellationpolicy_change"),
            args=(self.cancellation_policy_id, )),
            self.cancellation_policy.cancellation_type
        )
        return url

    def save(self, force_insert=False, force_update=False, **kwargs):
        super(ArtistPolicy, self).save(force_insert, force_update)
        if self.id:
            if self.status == 1:
                ArtistPolicy.objects.filter(artist=self.artist, status=1).exclude(id=self.id).update(status=2)

    artist_link.allow_tags = True
    artist_link.short_description = "Artist"

    cancellation_policy_link.short_description = 'Cancellation Type'
    cancellation_policy_link.allow_tags = True
