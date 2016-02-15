from django.db import models
from django.core.urlresolvers import reverse

from glamazer.artists.models import Artist
from glamazer.listings.models import Listing
from glamazer.booking.models import Booking
from glamazer.users.models import Profile


class Review(models.Model):
    client = models.ForeignKey(Profile)
    artist = models.ForeignKey(Artist)
    listing = models.ForeignKey(Listing)
    booking = models.ForeignKey(Booking)
    rating = models.FloatField()
    text = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def artist_link(self):
        url = '<a href="%s">%s</a>' % (reverse(("admin:artists_artist_change"), args=(self.artist_id, )), self.artist.user.first_name)
        return url

    def client_link(self):
        url = '<a href="%s">%s</a>' % (reverse(("admin:users_profile_change"), args=(self.client_id, )), self.client.user.first_name)
        return url

    def listing_link(self):
        url = '<a href="%s">%s</a>' % (reverse(("admin:listings_listing_change"), args=(self.listing_id, )), self.listing.title)
        return url

    def booking_link(self):
        url = '<a href="%s">%s</a>' % (reverse(("admin:booking_booking_change"), args=(self.booking_id, )), self.booking.__str__())
        return url

    artist_link.allow_tags = True
    artist_link.short_description = "Artist"

    client_link.allow_tags = True
    client_link.short_description = 'Client'

    listing_link.allow_tags = True
    listing_link.short_description = "Listing"

    booking_link.allow_tags = True
    booking_link.short_description = "Booking"


class WaitingForFeedback(models.Model):
    client = models.ForeignKey(Profile)
    artist = models.ForeignKey(Artist)
    listing = models.ForeignKey(Listing)
    booking = models.ForeignKey(Booking)
    token = models.CharField(max_length=128, blank=True, null=True)

    def artist_link(self):
        url = '<a href="%s">%s</a>' % (reverse(("admin:artists_artist_change"), args=(self.artist_id, )), self.artist.user.first_name)
        return url

    def client_link(self):
        url = '<a href="%s">%s</a>' % (reverse(("admin:users_profile_change"), args=(self.client_id, )), self.client.user.first_name)
        return url

    def listing_link(self):
        url = '<a href="%s">%s</a>' % (reverse(("admin:listings_listing_change"), args=(self.listing_id, )), self.listing.title)
        return url

    def booking_link(self):
        url = '<a href="%s">%s</a>' % (reverse(("admin:booking_booking_change"), args=(self.booking_id, )), self.booking.__str__())
        return url

    artist_link.allow_tags = True
    artist_link.short_description = "Artist"

    client_link.allow_tags = True
    client_link.short_description = 'Client'

    listing_link.allow_tags = True
    listing_link.short_description = "Listing"

    booking_link.allow_tags = True
    booking_link.short_description = "Booking"
