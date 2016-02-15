import json
import random
import string

from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_exempt

from glamazer.widget.models import ExternalToken
from glamazer.artists.models import Artist
from glamazer.listings.models import Listing
from glamazer.core.helpers import get_object_or_None


@xframe_options_exempt
def widget(request, token=None):
    token = get_object_or_None(ExternalToken, token=token)
    all_artists = []
    all_listings = []
    if not token:
        raise PermissionDenied
    user = token.user
    if user.related_with == 'artists':
        artist = user.artist
        widget = {
            "avatar": artist.get_avatar,
            "name": user.first_name,
            "related_with": user.related_with,
            "have_image": token.have_image,
        }
        listings = Listing.objects.filter(artist=artist, status=1)
        for l in listings:
            listing = {
                "id": l.id,
                "artist_id": l.artist_id,
                "title": l.title,
                "picture": l.get_picture,
                "price": l.price,
                "currency": l.get_currency_display,
                "duration": l.duration,
            }
            all_listings.append(listing)
        widget["listings"] = all_listings

    elif user.related_with == 'salons':
        salon = user.salon
        widget = {
            "avatar": salon.get_avatar,
            "name": user.first_name,
            "related_with": user.related_with,
            "have_image": token.have_image,
        }
        artists = Artist.objects.filter(salon=salon)
        for a in artists:
            artist = {
                "id": a.id,
                "name": a.user.first_name,
                "avatar": a.get_avatar,
            }
            all_artists.append(artist)

        listings = Listing.objects.filter(artist__in=artists, status=1)
        for l in listings:
            listing = {
                "id": l.id,
                "artist_id": l.artist_id,
                "title": l.title,
                "picture": l.get_picture,
                "price": l.price,
                "currency": l.get_currency_display,
                "duration": l.duration,
            }
            all_listings.append(listing)
        widget["listings"] = all_listings

    return render(request, 'widget/widget.html', {"widget": widget, "artists": all_artists})


@xframe_options_exempt
def create_widget(request):
    user = request.user
    token = get_object_or_None(ExternalToken, user=user)
    if not token:
        hash_name = ''.join(random.choice(string.ascii_lowercase + string.digits)for x in range(32))
        token = ExternalToken.objects.create(user=user, token=hash_name)
        token = token

    return render(request, user.related_with + '/management/widgets.html', {"token": token})


@xframe_options_exempt
def toggle_logo(request):
    user = request.user
    token = get_object_or_None(ExternalToken, user=user)
    if token.have_image:
        token.have_image = False
        token.save()
    else:
        token.have_image = True
        token.save()

    return HttpResponse(json.dumps("COMPLETE"), content_type="application/json")
