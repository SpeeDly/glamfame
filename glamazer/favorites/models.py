from django.db import models
from django.contrib.auth.models import User

from glamazer.listings.models import Listing


class Favorite(models.Model):
    user = models.ForeignKey(User)
    listing = models.ForeignKey(Listing)
    date = models.DateTimeField(auto_now_add=True)
