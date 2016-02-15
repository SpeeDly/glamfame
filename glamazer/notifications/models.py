import redis
from django.db import models
from django.http import HttpResponse, HttpResponseServerError
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from glamazer.core.helpers import current_time
from glamazer.settings import MEDIA_ROOT


class Notification(models.Model):
    sender = models.ForeignKey(User, related_name='sender')
    receiver = models.ForeignKey(User, related_name='receiver')
    time = models.IntegerField(default=current_time)
    short_text = models.TextField()
    long_text = models.TextField()
    is_readed = models.BooleanField(default=False)

    class Meta:
        ordering = ['-time']

    def sender_link(self):
        url = None
        if self.sender.related_with == 'profiles':
            url = '<a href="%s">%s</a>' % (reverse(("admin:users_profile_change"), args=(self.sender.profile.id, )), self.sender.first_name)
        elif self.sender.related_with == 'artists':
            url = '<a href="%s">%s</a>' % (reverse(("admin:artists_artist_change"), args=(self.sender.artist.id, )), self.sender.first_name)
        elif self.sender.related_with == 'salons':
            url = '<a href="%s">%s</a>' % (reverse(("admin:salons_salon_change"), args=(self.sender.salon.id, )), self.sender.first_name)
        return url

    def receiver_link(self):
        url = None
        if self.receiver.related_with == 'profiles':
            url = '<a href="%s">%s</a>' % (reverse(("admin:users_profile_change"), args=(self.receiver.profile.id, )), self.receiver.first_name)
        elif self.receiver.related_with == 'artists':
            url = '<a href="%s">%s</a>' % (reverse(("admin:artists_artist_change"), args=(self.receiver.artist.id, )), self.receiver.first_name)
        elif self.receiver.related_with == 'salons':
            url = '<a href="%s">%s</a>' % (reverse(("admin:salons_salon_change"), args=(self.receiver.salon.id, )), self.receiver.first_name)
        return url

    sender_link.allow_tags = True
    sender_link.short_description = "Sender"

    receiver_link.allow_tags = True
    receiver_link.short_description = "Receiver"


@receiver(post_save, sender=Notification)
def send_notifications(sender, instance, **kwargs):
    try:
        r = redis.StrictRedis(host='localhost', port=6379, db=0)
        receiver = instance.receiver
        if receiver.related_with == "artists" and receiver.artist.salon:
            r.publish('notification_count', str(receiver.artist.salon.user.id) + "___" + instance.long_text)

        r.publish('notification_count', str(receiver.id) + "___" + instance.long_text)
        return HttpResponse("Everything worked :)")
    except Exception as e:
        return HttpResponseServerError(str(e))


class Hint(models.Model):
    USER_GROUPS = ((0, "User"), (1, "Artist"), (2, "Salon"))
    group = models.IntegerField(default=0, choices=USER_GROUPS)
    title = models.CharField(max_length=128)
    media = models.ImageField(upload_to=MEDIA_ROOT+'/hints/')
    description = models.TextField()
    priority = models.IntegerField(default=0)
