import string
import random
import os
import base64
import re

from io import BytesIO
from PIL import Image

from django import forms
from django.utils.translation import ugettext as _

from glamazer.core.helpers import get_object_or_None
from glamazer.listings.models import Listing, Tags, ListingTags
from glamazer.settings import MEDIA_ROOT, DURATION


class EditListing(forms.Form):

    title = forms.CharField(required=True, widget=forms.TextInput())
    description = forms.CharField(required=True, widget=forms.TextInput())
    price = forms.CharField(required=True, widget=forms.NumberInput())
    tags = forms.CharField(required=True, widget=forms.TextInput(attrs={"class": "listing_edit", "value": " ", "data-option": "LONDON"}))
    duration = forms.ChoiceField(widget=forms.Select(), choices=DURATION)
    cover = forms.CharField(required=False, widget=forms.HiddenInput(), initial=0)
    gender = forms.ChoiceField(widget=forms.RadioSelect(), choices=((0, 'Male'), (2, 'Female')))
    deleted = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Listing

    def clean_price(self):
        data = self.cleaned_data
        price = data['price']
        if not (len(price) in range(5) and price.isdigit()):
            raise forms.ValidationError(_('Please enter a valid price.'))

        return price

    def save(self, listing, FILES):
        data = self.cleaned_data
        pictures = FILES.getlist('files')
        hash_name = ''.join(random.choice(string.ascii_lowercase + string.digits)for x in range(6))

        my_dir = MEDIA_ROOT + listing.picture[7:]

        deletes_files = data['deleted']
        if deletes_files:
            deletes_files = data['deleted'].split(',')[:-1]
            for d in deletes_files:
                os.remove(d)

        os.chdir(my_dir)

        cover = data["cover"]

        artist_id = str(listing.artist_id)

        for index, picture in enumerate(pictures):
            dataUrlPattern = re.compile('data:image/(png|jpeg);base64,(.*)$')
            my_file = dataUrlPattern.match(picture).group(2)

            hash_name = ''.join(random.choice(string.ascii_lowercase + string.digits)for x in range(6))

            if cover.isdigit() and index == int(cover):
                full_path = MEDIA_ROOT + 'artists/' + artist_id + '/listings/' + listing.metadata + '/' + hash_name + '.jpeg'
                cover = full_path
            else:
                full_path = MEDIA_ROOT + 'artists/' + artist_id + '/listings/' + listing.metadata + '/' + hash_name + '.jpeg'

            #if the folder doesn't exist, create on
            d = os.path.dirname(full_path)
            if not os.path.exists(d):
                os.makedirs(d)

            im = Image.open(BytesIO(base64.b64decode(my_file.encode('ascii'))))
            im.save(full_path, 'JPEG')

        ListingTags.objects.filter(listing=listing).delete()
        tags = data['tags'].split(',')
        for tag in tags:
            tag = tag.lower()
            current_tag = get_object_or_None(Tags, tag=tag)
            if not current_tag:
                current_tag = Tags.objects.create(tag=tag)

            ListingTags.objects.create(listing=listing, tags=current_tag)

        if cover:
            listing.picture_cover = cover
        listing.title = data['title']
        listing.description = data['description']
        listing.price = data['price']
        listing.duration = int(data['duration'])
        listing.gender = int(data['gender'])
        listing.save()

        return listing
