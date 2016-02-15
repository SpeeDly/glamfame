from haystack import indexes

from glamazer.listings.models import Listing


class ListingIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, use_template=False)
    listing_id = indexes.IntegerField(model_attr='id')
    artist_id = indexes.IntegerField(model_attr='get_artist_id')
    artist_avatar = indexes.CharField(model_attr='get_artist_avatar')
    artist_name = indexes.CharField(model_attr='get_artist_name')
    salon_id = indexes.IntegerField(model_attr='get_salon_id')
    salon_name = indexes.CharField(model_attr='get_salon_name')
    salon_avatar = indexes.CharField(model_attr='get_salon_avatar')
    title = indexes.NgramField(model_attr='title')
    location = indexes.LocationField(model_attr='get_location')
    description = indexes.NgramField(model_attr='description')
    get_picture = indexes.CharField(model_attr='get_picture')
    metadata = indexes.CharField(model_attr='metadata')
    currency = indexes.CharField(model_attr='currency')
    price = indexes.FloatField(model_attr='price')
    likes = indexes.IntegerField(model_attr='likes')
    comments = indexes.IntegerField(model_attr='comments')
    tags = indexes.NgramField(model_attr='get_tags')
    status = indexes.IntegerField(model_attr='status')
    gender = indexes.IntegerField(model_attr='gender')
    rating = indexes.IntegerField(model_attr='get_rating')
    style = indexes.NgramField(model_attr='get_style')

    def get_model(self):
        return Listing

    def index_queryset(self, using=None):
        return self.get_model().objects.all().select_related('artist')
