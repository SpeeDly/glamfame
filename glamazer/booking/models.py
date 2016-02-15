import datetime

from django.db import models
from django.core.urlresolvers import reverse

from glamazer.listings.models import Listing
from glamazer.artists.models import Artist, CancellationPolicy
from glamazer.users.models import Profile
from glamazer.settings import STATUS, CURRENCY


class Booking(models.Model):
    artist = models.ForeignKey(Artist, null=True)
    client = models.ForeignKey(Profile)
    listing = models.ForeignKey(Listing)
    cancellation_policy = models.ForeignKey(CancellationPolicy)
    currency = models.CharField(max_length=8, choices=CURRENCY, default='USD')
    price = models.FloatField(default=0)
    revenue = models.FloatField(default=0)
    title = models.TextField(blank=True, null=True)
    start_time = models.IntegerField(default=0)
    end_time = models.IntegerField(default=0)
    comment = models.TextField(blank=True, null=True)
    status = models.IntegerField(default=0, choices=STATUS)
    cancelled_by = models.IntegerField(default=0)
    review_email = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return datetime.datetime.fromtimestamp(self.start_time).strftime('%Y-%m-%d %H:%M:%S')

    def get_status(self):
        return self.get_status_display()

    def artist_link(self):
        url = '<a href="%s">%s</a>' % (reverse(("admin:artists_artist_change"), args=(self.artist_id, )), self.artist.user.first_name)
        return url

    def client_link(self):
        url = '<a href="%s">%s</a>' % (reverse(("admin:users_profile_change"), args=(self.client_id, )), self.client.user.first_name)
        return url

    def listing_link(self):
        url = '<a href="%s">%s</a>' % (reverse(("admin:listings_listing_change"), args=(self.listing_id, )), self.listing.title)
        return url

    artist_link.allow_tags = True
    artist_link.short_description = "Artist"

    client_link.short_description = 'Client'
    client_link.allow_tags = True

    listing_link.allow_tags = True
    listing_link.short_description = "Listing"


class DummyBooking(models.Model):
    artist = models.ForeignKey(Artist)
    client = models.ForeignKey(Profile)
    listing = models.ForeignKey(Listing)
    cancellation_policy = models.ForeignKey(CancellationPolicy)
    currency = models.CharField(max_length=8, choices=CURRENCY, default='USD')
    revenue = models.FloatField(default=0)
    price = models.FloatField(default=0)
    title = models.TextField(blank=True, null=True)
    start_time = models.IntegerField(default=0)
    end_time = models.IntegerField(default=0)
    description = models.TextField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)


class ReportedProblems(models.Model):
    _STATUS = ((0, 'Open',), (1, 'In progress',), (2, 'Closed',),)
    artist = models.ForeignKey(Artist, null=True)
    client = models.ForeignKey(Profile, null=True)
    listing = models.ForeignKey(Listing, null=True)
    booking = models.ForeignKey(Booking, null=True)
    comment = models.TextField(blank=True, null=True, default=0)
    created = models.DateTimeField(auto_now_add=True, null=True, default=0)
    sender = models.CharField(max_length=16, default=0, null=True)
    status = models.IntegerField(default=0, choices=_STATUS, null=True)
