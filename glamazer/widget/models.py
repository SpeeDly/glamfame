from django.db import models
from django.contrib.auth.models import User


class ExternalToken(models.Model):
    user = models.OneToOneField(User, unique=True)
    token = models.CharField(max_length=128, blank=True, null=True)
    have_image = models.BooleanField(default=True)
