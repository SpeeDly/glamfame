from django.db import models
from django.contrib.auth.models import User

from glamazer.notifications.models import Notification
from glamazer.settings import MEDIA_ROOT, STATIC_ROOT


class Profile(models.Model):

    facebook_id = models.CharField(max_length=20, blank=True, null=True)
    user = models.OneToOneField(User, unique=True)
    avatar = models.CharField(max_length=128, blank=True, null=True)
    auto_created = models.BooleanField(default=False)
    is_activated = models.BooleanField(default=False)
    mobile_number = models.CharField(max_length=128, blank=True, null=True)
    enable_emails = models.BooleanField(default=True)
    enable_sms = models.BooleanField(default=False)

    def __str__(self):
        return self.user.first_name

    def get_avatar(self):
        if self.avatar:
            return MEDIA_ROOT + self.avatar[7:]
        else:
            return ''

    def get_name(self):
        return self.user.first_name

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
        if self.avatar:
            return '<img src="%s" style="border-radius: 999px" />' % self.avatar
        else:
            return '<img src="%s" style="border-radius: 999px" />' % (STATIC_ROOT+'/img/default.png')

    get_avatar_tag.short_description = 'Avatar'
    get_avatar_tag.allow_tags = True

    get_name.allow_tags = True
    get_name.short_description = "Name"


class ConfirmationToken(models.Model):
    user = models.ForeignKey(User)
    email_token = models.CharField(max_length=32)


class PasswordToken(models.Model):
    email = models.CharField(max_length=255)
    email_token = models.CharField(max_length=255)


related_with = models.CharField(max_length=16, blank=True, null=True)
related_with.contribute_to_class(User, 'related_with')
