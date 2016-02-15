import os
import json
import string
import random
import shutil
import urllib.request

from time import strftime
from time import gmtime

from PIL import Image

from django.db.models import Sum
from django.http import HttpResponse, HttpResponseRedirect
from django.utils import simplejson
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _

from glamazer.settings import MEDIA_ROOT, MEDIA_FOLDER, MIN_WITHDRAW, HOURS, CURRENCY
from glamazer.core.helpers import login_user, get_object_or_None, paginator, current_time, IBAN_checker, get_rate, get_fee
from glamazer.core.notifications import welcome, accept_suspend_request, accept_work_request, reject_work_request, reject_suspend_request
from glamazer.salons.forms import SalonForm, LocationSalonDetails, EditSalon, AddArtist, UploadListing, EditArtist
from glamazer.artists.models import Artist, WorkTime, Busy, CancellationPolicy, ArtistPolicy
from glamazer.salons.models import Salon
from glamazer.listings.models import Listing, ListingView
from glamazer.booking.models import Booking
from glamazer.payments.models import ReceiverAccount, Withdraw
from glamazer.reviews.models import Review


def sign_up(request):
    if request.GET.get("step") == '2':
        if request.method == "POST":

            form = LocationSalonDetails(request.POST)

            if form.is_valid():
                data = form.cleaned_data
                Salon.objects.filter(user=request.user).update(lat=data["lat"],
                                                               lng=data["lng"],
                                                               step=0,)
                return HttpResponseRedirect(reverse('salons_profile')+"?show_hint=1")
        else:
            form = LocationSalonDetails()
    else:
        if request.method == "POST":

            request.GET.get("step")
            form = SalonForm(request.POST)

            if form.is_valid():
                data = form.cleaned_data
                form.save()
                user = authenticate(
                    email=data['email'], password=data['password'])
                artist = Salon.objects.create(user=user)
                ReceiverAccount.objects.create(user=user, paypal_email=user.email)

                if user is not None and user.is_active:
                    artist.step = 2
                    artist.save()
                    auth_login(request, user)
                    welcome(None, receiver=user)
                    return HttpResponseRedirect(reverse('salons_sign_up')+"?step=2")
        else:
            form = SalonForm()

    return render(request, 'salons/sign_up.html', {'form': form})


def facebook_registration(request):
    data = request.POST

    password = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(6))

    is_user = get_object_or_None(User, email=data['email'])

    if not is_user:
        username = ''.join(random.choice(string.ascii_lowercase + string.digits)for x in range(16))
        new_user = User.objects.create_user(username=username,
                                            first_name=data['name'],
                                            email=data['email'],
                                            password=password,
                                            related_with="salons")
        salon = Salon.objects.create(user=new_user, facebook_id=data['facebook_id'], step=2)
        ReceiverAccount.objects.create(user=new_user, paypal_email=new_user.email)

        hash_name = ''.join(random.choice(string.ascii_lowercase + string.digits)for x in range(10))
        path = '/' + MEDIA_FOLDER + '/salons/' + str(salon.id) + '/avatar/' + hash_name + '.jpeg'
        full_path = MEDIA_ROOT + 'salons/' + str(salon.id) + '/avatar/' + hash_name + '.jpeg'
        d = os.path.dirname(full_path)
        if not os.path.exists(d):
            os.makedirs(d)
        else:
            shutil.rmtree(d)
            os.makedirs(d)
        urllib.request.urlretrieve(data['avatar'], full_path)

        salon.avatar = path
        salon.save()

        welcome(None, new_user, password)

        login_user(request, new_user)
    else:
        raise Exception(_("Not registered"))


def gallery(request):
    files = request.FILES.getlist('file')
    salon = request.user.salon
    salon_id = str(salon.id)
    salon.step = 0
    salon.save()

    for f in files:
        hash_name = ''.join(random.choice(string.ascii_lowercase + string.digits)for x in range(10))
        full_path = MEDIA_ROOT + 'salons/' + str(salon_id) + '/gallery/' + hash_name + '.jpeg'

        # check if the directory existings
        d = os.path.dirname(full_path)
        if not os.path.exists(d):
            os.makedirs(d)

        im = Image.open(f)
        im.save(full_path, 'JPEG')

    return HttpResponse(simplejson.dumps("COMPLETE"), content_type="application/json")


@login_required
def edit(request):
    user = request.user
    salon = user.salon

    if request.method == 'POST':
        form = EditSalon(request.POST, request.FILES, instance=salon)
        if form.is_valid():
            form.save()

            return HttpResponseRedirect(reverse('salons_edit'))

    else:
        form = EditSalon(instance=salon,
                         initial={'name': user.first_name,
                                  'avatar': salon.avatar,
                                  'description': salon.description,
                                  'lat': salon.lat,
                                  'lng': salon.lng,
                                  'mobile_number': salon.mobile_number})

    return render(request, 'salons/settings/edit.html', {'salon': salon, "form": form})


def artists(request):
    artists = Artist.objects.filter(salon=request.user.salon)
    return render(request, 'salons/management/artists.html', {"artists": artists})


def photos(request):
    salon = request.user.salon
    pictures = salon.get_all_images()
    return render(request, 'salons/settings/gallery.html', {'pictures': pictures, 'salon': salon})


def profile(request, salon_id=None, name=None):
    if salon_id:
        salon = get_object_or_404(Salon, id=salon_id)
    else:
        user = request.user
        salon = get_object_or_404(Salon, user__id=user.id)

    listings = []

    _artists = Artist.objects.select_related("user").filter(salon=salon, is_activated=True, waiting_for_hired=False)
    artists = [a.id for a in _artists]
    listings = Listing.objects.filter(artist_id__in=artists, status=1)
    reviews = Review.objects.filter(artist_id__in=artists)
    rating = get_rate(reviews)
    return render(request, 'salons/profile.html', {'salon': salon,
                                                   'artists': _artists,
                                                   'reviews': reviews,
                                                   'rating': rating,
                                                   'listings': listings})


def delete_image(request):
    if request.method == 'POST':
        name = request.POST.get("name")
        os.remove('{0}salons/{1}/gallery/{2}'.format(MEDIA_ROOT, request.user.salon.id, name))
    return HttpResponse(simplejson.dumps("COMPLETE"), content_type="application/json")


def add_artist(request):
    salon = get_object_or_None(Salon, user=request.user)

    if request.method == 'POST':
        form = AddArtist(request.POST, request.FILES)
        if form.is_valid():
            artist = form.save(salon)
            WorkTime.objects.create(artist=artist)
            artists = Artist.objects.filter(salon=salon)
            if len(artists) > 1:
                cp_id = ArtistPolicy.objects.filter(artist=artists[0])[0]
                ArtistPolicy.objects.filter(artist=artist).update(cancellation_policy=cp_id.cancellation_policy, status=1)

            return HttpResponseRedirect(reverse('salons_profile'))

    else:
        form = AddArtist()

    return render(request, 'salons/add_artist.html', {'form': form})


def upload(request):
    salon = request.user.salon

    if request.method == 'POST':
        form = UploadListing(salon, request.POST, request=request)
        fee = get_fee()

        if form.is_valid():
            listing = form.save(request.POST)[0]
            messages.add_message(request, messages.INFO,
                _("Your listing %s has been successfully created and submitted for review. Your listing will go live within the next couple of hours.") % listing.title)
            return HttpResponseRedirect(reverse('salons_listings'))

    else:
        form = UploadListing(salon)
        fee = get_fee()
    return render(request, 'salons/upload.html', {'salon': salon, "form": form, "fee": fee})


def edit_artist(request, artist_id=None):
    artist = get_object_or_None(Artist, id=int(artist_id))
    user = artist.user

    if request.method == 'POST':
        form = EditArtist(request.POST, request.FILES, instance=artist)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('salons_artists_edit', kwargs={'artist_id': artist_id}))
    else:
        form = EditArtist(instance=artist,
                          initial={'name': user.first_name,
                                   'avatar': artist.avatar,
                                   'description': artist.description,
                                   'style': artist.style,
                                   'enable_emails': artist.enable_emails,
                                   'enable_sms': artist.enable_sms})

    return render(request, 'salons/artist_settings/edit_artist.html', {'artist': artist, "form": form})


def schedule(request, artist_id=None):
    artist = get_object_or_404(Artist, id=int(artist_id))
    _work_time = WorkTime.objects.get(artist=artist)
    work_time = {}
    work_time["mon_start"] = " " if _work_time.mon_start == -1 else HOURS[_work_time.mon_start]
    work_time["mon_end"] = " " if _work_time.mon_end == -1 else HOURS[_work_time.mon_end]
    work_time["tues_start"] = " " if _work_time.tues_start == -1 else HOURS[_work_time.tues_start]
    work_time["tues_end"] = " " if _work_time.tues_end == -1 else HOURS[_work_time.tues_end]
    work_time["wed_start"] = " " if _work_time.wed_start == -1 else HOURS[_work_time.wed_start]
    work_time["wed_end"] = " " if _work_time.wed_end == -1 else HOURS[_work_time.wed_end]
    work_time["thurs_start"] = " " if _work_time.thurs_start == -1 else HOURS[_work_time.thurs_start]
    work_time["thurs_end"] = " " if _work_time.thurs_end == -1 else HOURS[_work_time.thurs_end]
    work_time["fri_start"] = " " if _work_time.fri_start == -1 else HOURS[_work_time.fri_start]
    work_time["fri_end"] = " " if _work_time.fri_end == -1 else HOURS[_work_time.fri_end]
    work_time["sat_start"] = " " if _work_time.sat_start == -1 else HOURS[_work_time.sat_start]
    work_time["sat_end"] = " " if _work_time.sat_end == -1 else HOURS[_work_time.sat_end]
    work_time["sun_start"] = " " if _work_time.sun_start == -1 else HOURS[_work_time.sun_start]
    work_time["sun_end"] = " " if _work_time.sun_end == -1 else HOURS[_work_time.sun_end]
    if request.method == "POST":
        data = request.POST
        _work_time.mon_start = -1 if data["1"] == "-1" else HOURS.index(data["1"])
        _work_time.mon_end = -1 if data["2"] == "-1" else HOURS.index(data["2"])
        _work_time.tues_start = -1 if data["3"] == "-1" else HOURS.index(data["3"])
        _work_time.tues_end = -1 if data["4"] == "-1" else HOURS.index(data["4"])
        _work_time.wed_start = -1 if data["5"] == "-1" else HOURS.index(data["5"])
        _work_time.wed_end = -1 if data["6"] == "-1" else HOURS.index(data["6"])
        _work_time.thurs_start = -1 if data["7"] == "-1" else HOURS.index(data["7"])
        _work_time.thurs_end = -1 if data["8"] == "-1" else HOURS.index(data["8"])
        _work_time.fri_start = -1 if data["9"] == "-1" else HOURS.index(data["9"])
        _work_time.fri_end = -1 if data["10"] == "-1" else HOURS.index(data["10"])
        _work_time.sat_start = -1 if data["11"] == "-1" else HOURS.index(data["11"])
        _work_time.sat_end = -1 if data["12"] == "-1" else HOURS.index(data["12"])
        _work_time.sun_start = -1 if data["13"] == "-1" else HOURS.index(data["13"])
        _work_time.sun_end = -1 if data["14"] == "-1" else HOURS.index(data["14"])
        _work_time.save()

    return render(request, 'salons/artist_settings/schedule.html', {"work_time": work_time, "artist": artist})


def salon_schedule(request, artist_id=None):
    if artist_id == "None":
        salon = request.user.salon
        try:
            artist = Artist.objects.filter(salon=salon, is_activated=True)[0]
            return HttpResponseRedirect(reverse('salons_schedule', kwargs={'artist_id': artist.id}))
        except:
            messages.add_message(request, messages.INFO,
                'You cannot view the calendar, without have any artists.')
            return HttpResponseRedirect(reverse('salons_artists'))

    salon = request.user.salon
    artist_id = int(artist_id)
    artist = get_object_or_404(Artist, id=artist_id, salon=salon)

    _work_time = WorkTime.objects.get(artist=artist)
    work_time = {}
    work_time["mon_start"] = " " if _work_time.mon_start == -1 else HOURS[_work_time.mon_start]
    work_time["mon_end"] = " " if _work_time.mon_end == -1 else HOURS[_work_time.mon_end]
    work_time["tues_start"] = " " if _work_time.tues_start == -1 else HOURS[_work_time.tues_start]
    work_time["tues_end"] = " " if _work_time.tues_end == -1 else HOURS[_work_time.tues_end]
    work_time["wed_start"] = " " if _work_time.wed_start == -1 else HOURS[_work_time.wed_start]
    work_time["wed_end"] = " " if _work_time.wed_end == -1 else HOURS[_work_time.wed_end]
    work_time["thurs_start"] = " " if _work_time.thurs_start == -1 else HOURS[_work_time.thurs_start]
    work_time["thurs_end"] = " " if _work_time.thurs_end == -1 else HOURS[_work_time.thurs_end]
    work_time["fri_start"] = " " if _work_time.fri_start == -1 else HOURS[_work_time.fri_start]
    work_time["fri_end"] = " " if _work_time.fri_end == -1 else HOURS[_work_time.fri_end]
    work_time["sat_start"] = " " if _work_time.sat_start == -1 else HOURS[_work_time.sat_start]
    work_time["sat_end"] = " " if _work_time.sat_end == -1 else HOURS[_work_time.sat_end]
    work_time["sun_start"] = " " if _work_time.sun_start == -1 else HOURS[_work_time.sun_start]
    work_time["sun_end"] = " " if _work_time.sun_end == -1 else HOURS[_work_time.sun_end]
    if request.method == "POST":
        data = request.POST
        _work_time.mon_start = -1 if data["1"] == "-1" else HOURS.index(data["1"])
        _work_time.mon_end = -1 if data["2"] == "-1" else HOURS.index(data["2"])
        _work_time.tues_start = -1 if data["3"] == "-1" else HOURS.index(data["3"])
        _work_time.tues_end = -1 if data["4"] == "-1" else HOURS.index(data["4"])
        _work_time.wed_start = -1 if data["5"] == "-1" else HOURS.index(data["5"])
        _work_time.wed_end = -1 if data["6"] == "-1" else HOURS.index(data["6"])
        _work_time.thurs_start = -1 if data["7"] == "-1" else HOURS.index(data["7"])
        _work_time.thurs_end = -1 if data["8"] == "-1" else HOURS.index(data["8"])
        _work_time.fri_start = -1 if data["9"] == "-1" else HOURS.index(data["9"])
        _work_time.fri_end = -1 if data["10"] == "-1" else HOURS.index(data["10"])
        _work_time.sat_start = -1 if data["11"] == "-1" else HOURS.index(data["11"])
        _work_time.sat_end = -1 if data["12"] == "-1" else HOURS.index(data["12"])
        _work_time.sun_start = -1 if data["13"] == "-1" else HOURS.index(data["13"])
        _work_time.sun_end = -1 if data["14"] == "-1" else HOURS.index(data["14"])
        _work_time.save()

    artists = Artist.objects.filter(salon=salon, is_activated=True)
    artists = [a.id for a in artists]

    current_index = artists.index(artist_id)
    next = artists[0] if current_index + 1 == len(artists) else artists[current_index+1]
    prev = artists[-1] if current_index == 0 else artists[current_index-1]

    return render(request, 'salons/management/schedule.html', {"work_time": work_time,
                                                               "artist": artist,
                                                               "next": next,
                                                               "prev": prev})


def bookings(request):
    user = request.user
    salon = Salon.objects.get(user=user)
    artists = Artist.objects.filter(salon=salon)
    bookings = Booking.objects.select_related().filter(artist__in=artists).order_by('start_time').reverse()
    if request.method == 'POST':
        sn = request.POST.get('sn', None)
        sn_approve = request.POST.get('sn_approve', None)

        if sn:
            b = Booking.objects.get(id=int(sn))
            old_status = b.status
            b.status = 2
            b.cancelled_by = 1
            b.save(old_status)

        elif sn_approve:
            b = Booking.objects.get(id=int(sn_approve))
            old_status = b.status
            b.status = 1
            b.cancelled_by = 1
            b.save(old_status)

        return redirect(reverse('salons_bookings'))

    bookings = paginator(request, bookings, 10)

    return render(request, 'salons/bookings.html', {"bookings": bookings})


def all_listings(request):
    salon = request.user.salon
    artists = Artist.objects.filter(salon=salon, waiting_for_hired=False)
    listings = Listing.objects.filter(artist__in=artists)
    return render(request, 'salons/management/listings.html', {'listings': listings})


def account(request):
    return render(request, 'salons/settings/account.html', {"user": request.user})


def delete_artist(request, artist_id):
    artist = Artist.objects.select_related("salon").get(id=int(artist_id))
    listings = Listing.objects.filter(artist=artist)
    # the current time in seconds, so we can filter the booking by this
    now = current_time()
    bookings = Booking.objects.select_related('artist', 'artist__user', 'client__user', 'listing').filter(artist=artist, start_time__gt=now, status__in=[0, 1])

    # select all artist, assigned to this salon
    init_artists = Artist.objects.select_related('user').filter(~Q(id=artist.id), salon=artist.salon)

    # If the salon have artists, and the artist have listings and bookings
    if listings and bookings and init_artists:
        data = []
        # for each booking, we should find the artist which are available... not a easy one to do
        for b in bookings:
            weekday = int(strftime('%w', gmtime(b.start_time)))
            # for each booking, we will have specific group of artists, which will be able to take the booking
            artist_to_submit = []
            # we need only the ids of the artists, os we can easiely and fast search for them
            artists = [a.id for a in init_artists]

            # check if the artist work in this day. Currently we'll ignore the fact that the time could be not in his worktime
            days = ['mon_start', 'tues_start', 'wed_start', 'thurs_start', 'fri_start', 'sat_start', 'sun_start']
            kwargs = {days[weekday]: -1}
            work_time = WorkTime.objects.filter(artist_id__in=artists).exclude(**kwargs)
            artists = [a.artist_id for a in work_time]

            # check if he is busy, during the time of the booking
            busy_hours = Busy.objects.filter(artist_id__in=artists).exclude(
                Q(end_time__lt=b.start_time) | Q(start_time__gt=b.end_time))

            sub_artists = [a.artist_id for a in busy_hours]
            artists = [a for a in artists if a not in sub_artists]
            # check for other booking during this time
            temp_booking = Booking.objects.filter(artist_id__in=artists).exclude(
                Q(end_time__lt=b.start_time) | Q(start_time__gt=b.end_time))

            sub_artists = [a.artist_id for a in temp_booking]
            artists = [a for a in artists if a not in sub_artists]

            artists = Artist.objects.select_related("user").filter(id__in=artists)
            for a in artists:
                artist_to_submit.append(a)
            data.append({"data": b, "artists": artist_to_submit[:]})

        return render(request, 'salons/delete_artist.html', {"artist": artist, "bookings": data})

# If the artist doesn't have any bookings
    else:
        for l in listings:
            l.status = 2
            l.save()

        salon_user = artist.salon.user
        artist.salon = None
        artist.save()
        user = artist.user
        messages.add_message(request, messages.INFO,
            _('{0} is removed successfully from your salon.').format(user.first_name))
        accept_suspend_request(user, salon_user)
        return HttpResponseRedirect(reverse('salons_artists'))


def activate(request, artist_id):
    artist = Artist.objects.select_related("user").get(id=int(artist_id))
    listings = Listing.objects.filter(artist=artist)

    artist.is_activated = True
    artist.save()

    if listings:
        for l in listings:
            l.status = 1
            l.save()

    messages.add_message(request, messages.INFO,
        '{0} is activated.'.format(artist.user.first_name))
    return HttpResponseRedirect(reverse('salons_artists'))


def reassign(request):
    if request.method == "POST":
        data = request.POST['data']
        artist_id = request.POST['artist']
        artist = Artist.objects.get(id=int(artist_id))
        listings = Listing.objects.filter(artist=artist)
        for l in listings:
            l.status = 2
            l.save()

        artist.salon = None
        artist.save()

        data = json.loads(data)

        for d in data:
            booking = Booking.objects.get(id=int(d['booking_id']))
            action = int(d['action'])

            if action == 1:
                booking.artist_id = d['artist_id']
                booking.save()

            elif action == 2:
                booking.status = 2
                booking.save()

    return HttpResponseRedirect(reverse('salons_artists'))


def calendar(request, artist_id):
    if artist_id == "None":
        salon = request.user.salon
        try:
            artist = Artist.objects.filter(salon=salon, is_activated=True)[0]
            return HttpResponseRedirect(reverse('salons_calendar', kwargs={'artist_id': artist.id}))
        except:
            messages.add_message(request, messages.INFO,
                _('You cannot view the calendar, without have any artists.'))
            return HttpResponseRedirect(reverse('salons_artists'))

    if request.method == "POST":
        artist = get_object_or_404(Artist, id=int(artist_id))
        start_time = request.POST.get("start_time", None)
        end_time = request.POST.get("end_time", None)
        comment = request.POST.get("comment", None)
        if start_time and end_time:
            Busy.objects.create(
                artist=artist,
                start_time=start_time,
                end_time=end_time,
                comment=comment
                )
    elif request.method == "GET":
        elem_id = request.GET.get("id", None)
        if elem_id:
            busy = get_object_or_None(Busy, id=int(elem_id))
            if busy:
                busy.delete()

    salon = request.user.salon
    artist_id = int(artist_id)
    artist = get_object_or_404(Artist, id=artist_id, salon=salon)
    bookings = Booking.objects.select_related().filter(artist=artist, status__in=[0, 1])
    busy = Busy.objects.filter(artist=artist)

    artists = Artist.objects.filter(salon=salon, is_activated=True)
    artists = [a.id for a in artists]

    current_index = artists.index(artist_id)

    next = artists[0] if current_index + 1 == len(artists) else artists[current_index+1]
    prev = artists[-1] if current_index == 0 else artists[current_index-1]

    return render(request, 'salons/management/calendar.html', {"artist": artist,
                                                               "bookings": bookings,
                                                               "busy": busy,
                                                               "next": next,
                                                               "prev": prev})


def cancellation_policy(request):
    user = request.user
    salon = Salon.objects.get(user=user)
    artists = Artist.objects.filter(salon=salon)

    if len(artists) == 0:
        messages.add_message(request, messages.INFO,
            _("Please create an artist first and then you will be able to change your cancellation policy"))
        return HttpResponseRedirect(reverse('salons_artists'))
    elif request.method == "POST":
        data = int(request.POST.get("cancel_id", None))
        if data == -1:
            percent = request.POST.get("percent", None)
            days = request.POST.get("days", None)
            cp = CancellationPolicy.objects.filter(days_before=int(days), percent=int(percent))
            check_if_in_use = ArtistPolicy.objects.filter(status__in=[1, 2], cancellation_policy__in=cp)
            if cp and check_if_in_use:
                cp_id = int(cp[0]['id'])
                ArtistPolicy.objects.filter(artist__in=artists, status=1).update(status=2)
                for a in artists:
                    ArtistPolicy.objects.create(artist=a, cancellation_policy_id=cp_id, status=1)
                messages.add_message(request, messages.INFO,
                    "Your cancellation policy have been changed.")
            else:
                cp = CancellationPolicy.objects.create(days_before=int(days), percent=int(percent))
                for a in artists:
                    ArtistPolicy.objects.create(artist=a, cancellation_policy=cp, status=0)
                messages.add_message(request, messages.INFO,
                    _("Your request have been submited. We'll review your custom policy and will approve or disapprove it in the next 2 hours."))
        else:
            ArtistPolicy.objects.filter(artist__in=artists, status=1).update(status=2)
            for a in artists:
                ArtistPolicy.objects.create(artist=a, cancellation_policy_id=data, status=1)
            messages.add_message(request, messages.INFO,
                    _("Your cancellation policy have been changed."))

        return HttpResponseRedirect(reverse('salons_cancellation_policy'))

    artist_policy = ArtistPolicy.objects.select_related("cancellationpolicy").filter(artist=artists[0], status__in=[1, 2])
    current_id = [x.cancellation_policy_id for x in artist_policy if x.status == 1][0]
    artist_policy = [x.cancellation_policy for x in artist_policy if x.cancellation_policy_id not in range(5)]

    return render(request, 'salons/settings/cancellation_policy.html', {"cp": artist_policy, "current_id": current_id})


def payments(request):
    if request.method == "POST":
        user = request.user
        ra = ReceiverAccount.objects.get(user=user)
        radio_data = int(request.POST.get("cancel_id", None))
        if radio_data == 1:
            paypal_email = request.POST.get("paypal_email", None)

            try:
                validate_email(paypal_email)
                ra.paypal_email = paypal_email
                ra.method = 1
                ra.save()
                messages.add_message(request, messages.SUCCESS,
                    _("Your paypal email account have been changed successfully."))
            except ValidationError:
                messages.add_message(request, messages.ERROR,
                    _("Please enter a valid email address !"))

        elif radio_data == 2:
            data = request.POST
            bank_name = data.get("bank_name", None)
            branch = data.get("branch", None)
            payee = data.get("payee", None)
            IBAN = data.get("IBAN", None)
            swift = data.get("swift", None)
            if bank_name and branch and payee and IBAN and swift:
                try:
                    IBAN_checker(IBAN)
                    ra.bank_name = bank_name
                    ra.branch = branch
                    ra.payee = payee
                    ra.iban = IBAN
                    ra.swift = swift
                    ra.method = 0
                    ra.save()
                    messages.add_message(request, messages.SUCCESS, _("The bank account settings are changed."))
                except Exception as e:
                    a = e
                    messages.add_message(request, messages.ERROR, a)
            else:
                messages.add_message(request, messages.ERROR,
                    _("Please feel the boxes !"))
    else:
        user = request.user
        ra = ReceiverAccount.objects.get(user=user)

    return render(request, 'salons/settings/payments.html', {"ra": ra})


def stats(request):
    artists = Artist.objects.select_related().filter(salon=request.user.salon, waiting_for_hired=False)
    if not artists:
        messages.add_message(request, messages.INFO,
            _("Currently you don't have any stats recorded. Please create an artist first."))
        return redirect(reverse('salons_artists'))
    return render(request, 'salons/management/stats.html', {"artists": artists})


def get_chart_info(request):
    ''' lvc is a reference for listing view count'''
    ''' abc is a reference for all booking count'''
    ''' sbc is a reference for good booking count'''
    if request.method == 'GET':
        lvc, abc, sbc = [], [], []
        data = request.GET.getlist('interval[]')
        artist_id = request.GET.get('artist_id', None)
        artist = Artist.objects.get(id=artist_id)
        start_date = data[0]
        end_date = data[-1]

        listings_view = ListingView.objects.filter(listing__artist=artist, date__range=(start_date, end_date))

        listing_view_date = {}

        for x in listings_view:
            listing_view_date[str(x.date)] = x

        for i in data:
            if i in listing_view_date:
                lvc.append(listing_view_date[i].views)
            else:
                lvc.append(0)

        revenues = []
        for d in data:
            date = d.split("-")
            booking = Booking.objects.filter(artist=artist,
                                             created__year=date[0],
                                             created__month=date[1],
                                             created__day=date[2]).count()
            abc.append(booking)

            good_booking = Booking.objects.filter(artist=artist,
                                                  created__year=date[0],
                                                  created__month=date[1],
                                                  created__day=date[2],
                                                  status=1).count()
            sbc.append(good_booking)

            temp_books = Booking.objects.filter(artist=artist,
                                                created__year=date[0],
                                                created__month=date[1],
                                                created__day=date[2]).aggregate(Sum('revenue'))

            if temp_books['revenue__sum'] is None:
                revenues.append(0)
            else:
                revenues.append(temp_books['revenue__sum'])

        info = []
        temp_var = {}
        for i in range(len(lvc)):
            temp_var = {}
            temp_var["number"] = i
            temp_var["date"] = data[i]
            temp_var["listings_view"] = lvc[i]
            temp_var["inqueries"] = abc[i]
            temp_var["bookings"] = sbc[i]
            temp_var["revenues"] = revenues[i]
            info.append(temp_var)

    return HttpResponse(simplejson.dumps({"lvc": lvc, "abc": abc, "sbc": sbc, "info": info}), content_type="application/json")


def wallet(request):
    ''''''
    transactions, all_earnings, all_widthraws, avaible_funds = [], 0, 0, 0
    user = request.user
    salon = user.salon
    transactions = Withdraw.objects.filter(user=user)

    avaible_funds = salon.money
    currency = dict(CURRENCY)[salon.currency]

    for t in transactions:
        all_widthraws += t.money

    all_earnings = all_widthraws + salon.money

    return render(request, 'salons/wallet.html', {"transactions": transactions,
                                                  "all_earnings": all_earnings,
                                                  "all_widthraws": all_widthraws,
                                                  "avaible_funds": avaible_funds,
                                                  "currency": currency})


def withdraw(request):
    if request.method == "POST":
        data = request.POST.get("amount", None)
        user = request.user
        salon = user.salon

        if not(data and data.isdigit() and salon.money >= int(data) and int(data) >= MIN_WITHDRAW ):
            messages.add_message(request, messages.ERROR,
                _("Please enter a valid amount."))
            return redirect(reverse("salons_withdraw"))
        else:
            salon.money = salon.money-int(data)
            salon.save()
            option = ReceiverAccount.objects.filter(user=user)[0]
            Withdraw.objects.create(user=user,
                                    option=option,
                                    money=round(float(data), 2),
                                    method=option.method)
            return redirect(reverse("salons_wallet"))

    user = request.user
    salon = user.salon
    if salon.money < MIN_WITHDRAW:
        messages.add_message(request, messages.ERROR,
            _("You need to earn at least $30 to proceed with the withdrawal request."))
        return redirect(reverse("salons_wallet"))

    money = salon.money

    return render(request, 'salons/withdraw.html', {"money": money})


def artists_accept(request, artist_id):
    artist = Artist.objects.select_related("users").get(id=artist_id)
    artist.waiting_for_hired = False
    artist.save()
    user = artist.user
    messages.add_message(request, messages.SUCCESS, _("You accepted {0} membership request").format(user.first_name))
    print(user.first_name, artist.salon.user.first_name)
    accept_work_request(artist.salon.user, user)
    return redirect(reverse('salons_artists'))


def artists_reject(request, artist_id):
    artist = Artist.objects.select_related("users").get(id=artist_id)
    salon_user = artist.salon.user
    artist.waiting_for_hired = False
    artist.salon = None
    artist.save()
    user = artist.user
    messages.add_message(request, messages.SUCCESS, _("You declined {0} membership request.").format(user.first_name))
    reject_work_request(salon_user, user)
    return redirect(reverse('salons_artists'))


def artists_reject_fire(request, artist_id):
    artist = Artist.objects.select_related("users").get(id=artist_id)
    artist.waiting_for_fired = False
    artist.save()
    user = artist.user
    messages.add_message(request, messages.SUCCESS, _("You declined {0}'s suspension request").format(user.first_name))
    reject_suspend_request(artist.salon.user, user)
    return redirect(reverse('salons_artists'))
