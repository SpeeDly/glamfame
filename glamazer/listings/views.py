import string
import random
import calendar
import time

from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils import simplejson
from django.utils.translation import ugettext as _

from glamazer.core.helpers import get_object_or_None, current_time, get_rate, login_user
from glamazer.core.emails import send_email
from glamazer.listings.models import Listing, ListingTags, ListingView
from glamazer.listings.forms import EditListing
from glamazer.users.models import Profile
from glamazer.artists.models import Artist, WorkTime, Busy, ArtistPolicy
from glamazer.favorites.models import Favorite
from glamazer.booking.models import DummyBooking, Booking
from glamazer.reviews.models import Review


def show(request, listing_id=None, title=None):

    if listing_id and listing_id.isdigit():
        try:
            listing = Listing.objects.select_related().get(id=int(listing_id))
        except:
            raise Http404
    else:
        raise Http404

    if listing.status == 3:
        raise Http404

    artist = listing.artist

    booked = False
    profile = None
    favorite = False

    ''' In case that the user start the booking '''
    if request.method == 'POST':
        ''' A hook for the case where the user is not logged in '''
        user = request.user
        back_url = request.POST.get("back_url", None)
        if user.is_authenticated() and not back_url:
            client = user.profile
        else:
            email = request.POST.get('email')
            user = get_object_or_None(User, email=email)
            if user:
                client = get_object_or_None(Profile, user=user)
                if client is not None:
                    login_user(request, user)
                else:
                    messages.add_message(request, messages.ERROR,
                        _("This email is already used by a beauty artist or salon. Please submit different email address in order to continue."))
                    return redirect(reverse('listing', kwargs={"listing_id": listing.id}))
            else:
                username = ''.join(random.choice(string.ascii_lowercase + string.digits)for x in range(16))
                password = ''.join(random.choice(string.ascii_lowercase + string.digits)for x in range(6))
                new_user = User.objects.create_user(username=username,
                                                    first_name='anonymous',
                                                    email=email,
                                                    password=password,
                                                    related_with="profiles",)
                client = Profile.objects.create(user=new_user, auto_created=True)
                kwargs = {}
                kwargs['password'] = password
                send_email(case=18, receiver=new_user, **kwargs)

        get_time = int(request.POST.get('time'))
        artist_policy = ArtistPolicy.objects.get(artist=artist, status=1)
        dummy_booking = DummyBooking.objects.create(artist=listing.artist,
                                                    listing=listing,
                                                    client=client,
                                                    cancellation_policy=artist_policy.cancellation_policy,
                                                    revenue=listing.price-listing.original_price,
                                                    price=listing.price,
                                                    title=listing.title,
                                                    start_time=get_time,
                                                    end_time=get_time + listing.duration,)

        request.session["dummy_booking_id"] = dummy_booking.id
        request.session["back_url"] = back_url
        return HttpResponseRedirect(reverse('booking_confirm'))

    else:
        ''' Just for reendering the page '''
        try:
            user = request.user
            favorite = get_object_or_None(Favorite, user=user, listing=listing)
            profile = get_object_or_None(Profile, user=user)
        except:
            pass
        # if current visiter is profile and the listing is not in his favorite list, the flag is turned on

        if not favorite and profile:
            favorite = False
        else:
            favorite = True

        # if current visiter is profile, we will give them a chance to book it
        if profile:
            bookings = Booking.objects.filter(client=profile, listing=listing)
            if bookings:
                for b in bookings:
                    if b.end_time > current_time() and b.status in [0, 1]:
                        booked = b.start_time

        hours = ['8:00 AM', '8:30 AM', '9:00 AM', '9:30 AM', '10:00 AM', '10:30 AM', '11:00 AM', '11:30 AM', '12:00 PM', '12:30 PM', '13:00 PM', '13:30 PM', '14:00 PM', '14:30 PM', '15:00 PM', '15:30 PM', '16:00 PM', '16:30 PM', '17:00 PM', '17:30 PM', '18:00 PM', '18:30 PM', '19:00 PM', '19:30 PM']
        artist_policy = ArtistPolicy.objects.get(artist=artist, status=1)
        tags = ListingTags.objects.select_related("tags").filter(listing=listing)
        tags = [t.tags.tag for t in tags]

        reviews = Review.objects.select_related().filter(listing=listing)
        reviews = list(reviews)
        rate = get_rate(reviews)
        artist_reviews = Review.objects.select_related().filter(artist=artist)
        artist_reviews = list(artist_reviews)
        artist_rate = get_rate(artist_reviews)

        current_date = time.strftime("%Y-%m-%d")

        listing_view, created = ListingView.objects.get_or_create(listing=listing, date=current_date)
        listing_view.views = listing_view.views + 1
        listing_view.save()

    return render(request, 'listings/details.html', {'listing': listing,
                                                     'artist': artist,
                                                     'reviews': reviews,
                                                     'rate': rate,
                                                     'artist_rate': artist_rate,
                                                     'favorite': favorite,
                                                     'hours': hours,
                                                     'booked': booked,
                                                     'policy': artist_policy,
                                                     'tags': tags})


def confirm(request):
    sn = request.session.get('dummy_booking_id', None)
    if sn:
        dummy_booking = get_object_or_None(DummyBooking, id=int(sn))
    else:
        raise Http404

    return render(request, 'listings/confirm.html', {'booking': dummy_booking})


def check_availability(request):
    busy_time = []
    booked = []

    if request.method == "POST":
        data = request.POST
        artist = Artist.objects.get(id=int(data["artist_id"]))
        work_time = WorkTime.objects.get(artist=artist)
        week_day = int(data["week_day"])
        year = int(data["year"])
        month = int(data["month"])
        day = int(data["date"])

        if week_day == 0:
            if work_time.sun_start == -1:
                start_time = "Time"
            else:
                start_time = work_time.sun_start
                end_time = work_time.sun_end
        elif week_day == 1:
            if work_time.mon_start == -1:
                start_time = "Time"
            else:
                start_time = work_time.mon_start
                end_time = work_time.mon_end
        elif week_day == 2:
            if work_time.tues_start == -1:
                start_time = "Time"
            else:
                start_time = work_time.tues_start
                end_time = work_time.tues_end
        elif week_day == 3:
            if work_time.wed_start == -1:
                start_time = "Time"
            else:
                start_time = work_time.wed_start
                end_time = work_time.wed_end
        elif week_day == 4:
            if work_time.thurs_start == -1:
                start_time = "Time"
            else:
                start_time = work_time.thurs_start
                end_time = work_time.thurs_end
        elif week_day == 5:
            if work_time.fri_start == -1:
                start_time = "Time"
            else:
                start_time = work_time.fri_start
                end_time = work_time.fri_end
        elif week_day == 6:
            if work_time.sat_start == -1:
                start_time = "Time"
            else:
                start_time = work_time.sat_start
                end_time = work_time.sat_end
        if start_time == "Time":
            busy_time = [x for x in range(0, 25)]
            booked = []
        else:
            busy_time = [x for x in range(0, start_time)] + [x for x in range(end_time, 24)]

            border_range_start = calendar.timegm((year, month+1, day, 2, 59, 59))
            border_range_end = calendar.timegm((year, month+1, day, 20, 0, 1))

            bookings = Booking.objects.filter(artist=artist,
                                              start_time__gte=border_range_start,
                                              start_time__lte=border_range_end,
                                              status__in=[0, 1])
            busy = Busy.objects.filter(artist=artist,
                                       start_time__gte=border_range_start,
                                       start_time__lte=border_range_end,)

            booked = []
            for b in bookings:
                booked.append({"start_time": b.start_time, "duration": b.end_time - b.start_time})

            for b in busy:
                booked.append({"start_time": b.start_time, "duration": b.end_time - b.start_time})

    return HttpResponse(simplejson.dumps({"busy_time": busy_time, "booked": booked}), content_type="application/json")


def edit(request, listing_id):
    listing = Listing.objects.get(id=int(listing_id))
    if request.method == "POST":
        form = EditListing(request.POST)
        if form.is_valid():
            listing = form.save(listing, request.POST)
            return HttpResponseRedirect(reverse('listing', kwargs={'listing_id': listing.id, "title": listing.title}))
    else:
        form = EditListing(initial={'title': listing.title,
                                    'description': listing.description,
                                    'price': round(listing.price),
                                    'tags': "",
                                    'duration': listing.duration,
                                    'gender': listing.gender,
                                    'cover': ""})
    tags = listing.get_tags()
    return render(request, 'listings/edit.html', {'form': form,
                                                 'listing': listing,
                                                 'tags': tags})


def delete(request, listing_id):
    listing = Listing.objects.get(id=int(listing_id))
    listing.status = 2
    listing.save()

    if request.user.related_with == 'artists':
        return HttpResponseRedirect(reverse('all_listing'))
    else:
        return HttpResponseRedirect(reverse('salons_listings'))


def activate(request, listing_id):
    listing = Listing.objects.get(id=int(listing_id))
    listing.status = 1
    listing.save()
    if request.user.related_with == 'artists':
        return HttpResponseRedirect(reverse('all_listing'))
    else:
        return HttpResponseRedirect(reverse('salons_listings'))
