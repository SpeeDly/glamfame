import os
import re
import math
import string
import random
import shutil
import base64

from io import BytesIO
from PIL import Image

from django import forms
from django.contrib.auth.models import User
from django.forms import ModelForm
from django.utils.translation import ugettext as _

from glamazer.core.helpers import get_object_or_None, get_fee
from glamazer.artists.models import Artist
from glamazer.listings.models import Listing, Tags, ListingTags
from glamazer.settings import STYLE_INDEXES, MEDIA_FOLDER, MEDIA_ROOT, DURATION


class ArtistForm(ModelForm):
    name = forms.CharField(required=True, widget=forms.TextInput())
    email = forms.EmailField(required=True, widget=forms.TextInput())
    password = forms.CharField(widget=(forms.PasswordInput()))
    confirm_password = forms.CharField(widget=(forms.PasswordInput()))

    class Meta:
        model = Artist
        fields = ['confirm_password', ]

    def clean_email(self):

        email = self.cleaned_data['email']
        check_email = User.objects.filter(email=email)

        if check_email:
            raise forms.ValidationError(
                _("A user associated with this email address already exists"))

        return email

    def clean_password(self):

        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')

        if not password == confirm_password:
            raise forms.ValidationError(_("Password mismatch"))

        elif len(password) < 6:
            raise forms.ValidationError(_("Password is too short (6 symbols)"))

        elif password.isalpha() or password.isdigit():
            raise forms.ValidationError(_("Password should contain at least one alphabetic and one non-alphabetic character"))

        return password

    def save(self):

        data = self.cleaned_data
        username = ''.join(random.choice(string.ascii_lowercase + string.digits)for x in range(16))

        new_user = User.objects.create_user(
            username=username,
            first_name=data['name'],
            email=data['email'],
            password=data['password'],
            related_with='artists',
            )

        return new_user


class LocationArtistDetails(forms.Form):
    style = forms.ChoiceField(widget=forms.Select(), choices=STYLE_INDEXES)
    address = forms.CharField(required=True, widget=forms.TextInput(attrs={'placeholder': _('Enter street address')}))
    lat = forms.CharField(required=True, widget=forms.HiddenInput())
    lng = forms.CharField(required=False, widget=forms.HiddenInput())


class EditArtist(ModelForm):
    name = forms.CharField(required=True, widget=forms.TextInput())
    avatar = forms.ImageField(required=False, widget=forms.FileInput())
    description = forms.CharField(required=False, widget=forms.Textarea())
    address = forms.CharField(required=False, max_length=128, widget=forms.TextInput())
    style = forms.ChoiceField(widget=forms.Select(), choices=STYLE_INDEXES)
    lat = forms.CharField(required=False, widget=forms.HiddenInput())
    lng = forms.CharField(required=False, widget=forms.HiddenInput())
    mobile_number = forms.CharField(required=False)
    cropped_image = forms.CharField(required=False, widget=forms.HiddenInput())
    enable_emails = forms.BooleanField(required=False)
    enable_sms = forms.BooleanField(required=False)

    class Meta:
        model = Artist
        exclude = ('money', 'rating', 'avatar', 'user', 'salon', 'step', 'currency')

    def clean_enable_sms(self):
        artist = self.instance
        enable_sms = self.cleaned_data.get('enable_sms')
        if enable_sms and not (artist.mobile_number or self.cleaned_data.get('mobile_number')):
            raise forms.ValidationError(_("Please enter your phone in order to receive sms."))

        return enable_sms

    def save(self):

        artist = self.instance
        user = artist.user
        data = self.cleaned_data

        user.first_name = data['name']
        user.save()

        my_file = data['cropped_image']

        if my_file:

            dataUrlPattern = re.compile('data:image/(png|jpeg);base64,(.*)$')
            my_file = dataUrlPattern.match(my_file).group(2)

            hash_name = ''.join(random.choice(string.ascii_lowercase + string.digits)for x in range(10))
            path = '/' + MEDIA_FOLDER + '/artists/' + str(user.artist.id) + '/avatar/' + hash_name + '.jpeg'
            full_path = MEDIA_ROOT + 'artists/' + str(user.artist.id) + '/avatar/' + hash_name + '.jpeg'

            artist.avatar = path
            artist.enable_sms = data["enable_sms"]
            artist.enable_emails = data["enable_emails"]
            artist.save()

            #if the folder doesn't exist, create one
            d = os.path.dirname(full_path)
            if not os.path.exists(d):
                os.makedirs(d)
            else:
                shutil.rmtree(d)
                os.makedirs(d)

            im = Image.open(BytesIO(base64.b64decode(my_file.encode('ascii'))))
            im.save(full_path, 'JPEG')

        else:
            artist.description = data['description']
            artist.address = data['address']
            artist.style = int(data['style'])
            artist.lat = data['lat']
            artist.lng = data['lng']
            artist.mobile_number = data['mobile_number']
            artist.enable_sms = data["enable_sms"]
            artist.enable_emails = data["enable_emails"]
            artist.save()
        return artist


class UploadListing(forms.Form):

    title = forms.CharField(required=True, widget=forms.TextInput())
    description = forms.CharField(required=True, widget=forms.Textarea(attrs={'placeholder': _('Enter description here.')}))
    price = forms.CharField(required=True, widget=forms.NumberInput())
    tags = forms.CharField(required=True, widget=forms.TextInput())
    duration = forms.ChoiceField(widget=forms.Select(), choices=DURATION)
    gender = forms.ChoiceField(widget=forms.RadioSelect(), choices=((0, _('Male')), (2, _('Female'))))
    cover = forms.CharField(required=False, widget=forms.HiddenInput(), initial=0)

    class Meta:
        model = Listing

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(UploadListing, self).__init__(*args, **kwargs)

    def clean_price(self):
        data = self.cleaned_data
        price = data['price']
        if not (len(price) in range(5) and price.isdigit()):
            raise forms.ValidationError(_('Please enter a valid price.'))

        return price

    def clean_cover(self):
        data = self.cleaned_data
        cover = data['cover']
        pictures = self.request.POST.getlist('files')
        if not pictures:
            raise forms.ValidationError(_('Please upload a valid image.'))

        return cover

    def save(self, artist, FILES):
        data = self.cleaned_data
        artist_id = str(artist.id)
        pictures = FILES.getlist('files')
        hash_name = ''.join(random.choice(string.ascii_lowercase + string.digits)for x in range(6))

        for index, picture in enumerate(pictures):

            dataUrlPattern = re.compile('data:image/(png|jpeg);base64,(.*)$')
            my_file = dataUrlPattern.match(picture).group(2)

            path = '/' + MEDIA_FOLDER + '/artists/' + artist_id + '/listings/' + hash_name + '/'
            if index == int(data["cover"]):
                full_path = MEDIA_ROOT + 'artists/' + artist_id + '/listings/' + hash_name + '/' + str(index) + '.jpeg'
                cover = full_path
            else:
                full_path = MEDIA_ROOT + 'artists/' + artist_id + '/listings/' + hash_name + '/' + str(index) + '.jpeg'

            #if the folder doesn't exist, create one
            d = os.path.dirname(full_path)
            if not os.path.exists(d):
                os.makedirs(d)

            im = Image.open(BytesIO(base64.b64decode(my_file.encode('ascii'))))
            im.save(full_path, 'JPEG')

        price = math.ceil(int(data['price'])*(1 + (get_fee(artist)/100)))

        listing = Listing.objects.create(
            artist=artist,
            picture=path,
            title=data['title'],
            description=data['description'],
            picture_cover=cover,
            original_price=data['price'],
            price=price,
            metadata=hash_name,
            gender=data['gender'],
            duration=int(data['duration']),
        )

        tags = data['tags'].split(',')
        tags.append(artist.get_style_display())
        for tag in tags:
            tag = tag.lower()
            current_tag = get_object_or_None(Tags, tag=tag)
            if not current_tag:
                current_tag = Tags.objects.create(tag=tag)

            ListingTags.objects.create(listing=listing, tags=current_tag)
        listing.save()
        return listing
