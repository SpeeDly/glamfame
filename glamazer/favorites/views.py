from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from glamazer.core.helpers import get_object_or_None
from glamazer.core.notifications import add_to_wishlist
from glamazer.listings.models import Listing
from glamazer.favorites.models import Favorite


def add(request, listing_id):
    listing_id = int(listing_id)
    user = request.user
    listing = Listing.objects.select_related("artist").get(id=listing_id)

    flag = get_object_or_None(Favorite, user=user, listing=listing)

    if not flag:
        listing.likes = listing.likes + 1
        listing.save()
        Favorite.objects.create(user=user, listing=listing)
        add_to_wishlist(user, listing.artist.user, listing)
    else:
        listing.likes = listing.likes - 1
        listing.save()
        flag.delete()

    return HttpResponseRedirect(reverse('listing', kwargs={'listing_id': listing.id, 'title': listing.title}))
