import os

from pyelasticsearch import ElasticSearch

from haystack.utils.geo import Point
from sorl.thumbnail import get_thumbnail

from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_save

from glamazer.settings import MEDIA_ROOT, ELASTIC_SEARCH_URL, LISTING_STATUS, CURRENCY
from glamazer.core.helpers import get_rate
from glamazer.core.notifications import new_listing, approved_listing, bad_listing
from glamazer.artists.models import Artist


class Listing(models.Model):
    artist = models.ForeignKey(Artist)
    picture = models.CharField(max_length=128, help_text='The path to the images. Never change it.')
    picture_cover = models.CharField(max_length=128)
    title = models.CharField(max_length=128)
    description = models.TextField()
    currency = models.CharField(max_length=8, choices=CURRENCY, default='USD')
    original_price = models.FloatField()
    price = models.FloatField()
    gender = models.IntegerField(choices=((0, 'Male'), (2, 'Female')))
    likes = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)
    metadata = models.CharField(max_length=16)
    duration = models.IntegerField(default=0, help_text="1800=00:30 | 3600=1:00 | 5400=1:30 | 7200=2:00 | 9000=2:30 | 10800=3:00 | 12600=3:30 | 14400=4:00")
    status = models.IntegerField(default=0, choices=LISTING_STATUS)
    uploaded = models.DateTimeField(auto_now_add=True)
    last_changed = models.DateTimeField(auto_now=True, auto_now_add=True)

    def __str__(self):
        return self.title

    def get_style(self):
        return self.artist.get_style_display()

    def get_picture(self):
        return self.picture_cover

    def get_all_pictures(self):
        pictures = []
        cover = self.picture_cover.split("/")[-1]
        full_path = MEDIA_ROOT + self.picture[7:]
        for p in os.listdir(full_path):
            if not p == cover:
                pictures.append(full_path + p)
        return pictures

    def get_location(self):
        return Point(self.artist.lat, self.artist.lng)

    def get_artist_id(self):
        return self.artist_id

    def get_artist_avatar(self):
        return self.artist.get_avatar()

    def get_artist_name(self):
        return self.artist.get_name()

    def get_salon_id(self):
        return self.artist.salon_id

    def get_salon_avatar(self):
        return self.artist.get_salon_avatar()

    def get_salon_name(self):
        return self.artist.get_salon_name()

    def get_tags(self):
        listings = ListingTags.objects.filter(listing=self).select_related("tags")
        return [x.tags.tag for x in listings]

    def get_rating(self):
        from glamazer.reviews.models import Review
        reviews = Review.objects.select_related().filter(listing=self)
        rate = get_rate(reviews)
        return rate

    def view_all_pictures(self):
        all_pictures = self.get_all_pictures()
        all_pictures.append(self.get_picture())
        thumbs = '<ul>'
        for pic in all_pictures:
            thumbs += '<li><img src="'
            thumbs += get_thumbnail(pic, '240x143', crop='center', quality=99).url
            thumbs += '"/></li>'
        return thumbs

    view_all_pictures.allow_tags = True
    view_all_pictures.short_description = "Pictures"

    def save(self, force_insert=False, force_update=False, **kwargs):
        es = ElasticSearch(ELASTIC_SEARCH_URL)
        if self.id:
            location = self.get_location()
            location_es = "{0},{1}".format(location.y, location.x)
            es.update('glamazer',
                      'modelresult',
                      'listings.listing.{0}'.format(self.id),
                      script="ctx._source.listing_id = listing;" +
                             "ctx._source.artist_id = artist;" +
                             "ctx._source.artist_avatar = artist_avatar;" +
                             "ctx._source.artist_name = artist_name;" +
                             "ctx._source.salon_id = salon;" +
                             "ctx._source.salon_avatar = salon_avatar;" +
                             "ctx._source.salon_name = salon_name;" +
                             "ctx._source.title = title;" +
                             "ctx._source.location = location;" +
                             "ctx._source.description = description;" +
                             "ctx._source.get_picture = get_picture;" +
                             "ctx._source.metadata = metadata;" +
                             "ctx._source.gender = gender;" +
                             "ctx._source.price = price;" +
                             "ctx._source.currency = currency;" +
                             "ctx._source.likes = likes;" +
                             "ctx._source.comments = comments;" +
                             "ctx._source.tags = tags;" +
                             "ctx._source.status = status;" +
                             "ctx._source.style = style;" +
                             "ctx._source.rating = rating",
                      params={
                             'listing': self.id,
                             'artist': self.get_artist_id(),
                             'artist_avatar': self.get_artist_avatar(),
                             'artist_name': self.get_artist_name(),
                             'salon': self.get_salon_id(),
                             'salon_avatar': self.get_salon_avatar(),
                             'salon_name': self.get_salon_name(),
                             'title': self.title,
                             'location': location_es,
                             'description': self.description,
                             'get_picture': self.get_picture(),
                             'metadata': self.metadata,
                             'gender': self.gender,
                             'price': self.price,
                             'currency': self.currency,
                             'likes': self.likes,
                             'comments': self.comments,
                             'tags': self.get_tags(),
                             'status': self.status,
                             'style': self.get_style(),
                             'rating': self.get_rating()
                        })
            super(Listing, self).save(force_insert, force_update)
        else:
            super(Listing, self).save(force_insert, force_update)

            location = self.get_location()
            location_es = "{0},{1}".format(location.y, location.x)
            es.index('glamazer', 'modelresult', {
                'listing_id': self.id,
                'artist_id': self.artist_id,
                'artist_avatar': self.get_artist_avatar(),
                'artist_name': self.get_artist_name(),
                'salon_id': self.get_salon_id(),
                'salon_avatar': self.get_salon_avatar(),
                'salon_name': self.get_salon_name(),
                'title': self.title,
                'location': location_es,
                'description': self.description,
                'get_picture': self.get_picture(),
                'metadata': self.metadata,
                'gender': self.gender,
                'price': self.price,
                'currency': self.currency,
                'likes': self.likes,
                'comments': self.comments,
                'tags': self.get_tags(),
                'status': self.status,
                'style': self.get_style(),
                'rating': self.get_rating()
                }, id='listings.listing.{0}'.format(self.id))
            es.refresh('glamazer')


@receiver(pre_save, sender=Listing)
def listing_change_status(sender, instance, **kwargs):
    if instance.id:
        old = Listing.objects.get(id=instance.id)
        if old.status == 0:
            if instance.status == 1:
                new_listing(instance.artist.user, None, instance)
                approved_listing(instance.artist.user, instance.artist.user, instance)
            else:
                bad_listing(instance.artist.user, instance.artist.user, instance)


class Tags(models.Model):
    tag = models.TextField()


class ListingTags(models.Model):
    listing = models.ForeignKey(Listing)
    tags = models.ForeignKey(Tags)


class ListingView(models.Model):
    listing = models.ForeignKey(Listing)
    date = models.DateField(auto_now_add=True)
    views = models.IntegerField(default=0)
