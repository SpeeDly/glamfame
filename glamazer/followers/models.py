from django.db import models
from django.contrib.auth.models import User

from glamazer.artists.models import Artist


class Followers(models.Model):
    user = models.ForeignKey(User)
    artist = models.ForeignKey(Artist)
    date = models.DateTimeField(auto_now_add=True)
