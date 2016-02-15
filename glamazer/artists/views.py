import string
import random
import os
import shutil
import urllib.request


from django.db.models import Sum
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils import simplejson
from django.utils.translation import ugettext as _

from glamazer.settings import MIN_WITHDRAW, MEDIA_ROOT, MEDIA_FOLDER
from glamazer.core.emails import send_email
from glamazer.core.notifications import start_following, accept_booking_request, decline_booking_request, cancel_booking_request, apply_for_salon, suspend_from_salon
from glamazer.core.helpers import login_user, get_object_or_None, paginator, void_authorization, IBAN_checker, get_rate, get_fee
from glamazer.artists.forms import EditArtist, ArtistForm, LocationArtistDetails, UploadListing
from glamazer.artists.models import Artist, Busy, WorkTime, ArtistPolicy, CancellationPolicy
from glamazer.listings.models import Listing, ListingView
from glamazer.followers.models import Followers
from glamazer.booking.models import Booking
from glamazer.payments.models import ReceiverAccount, Withdraw
from glamazer.reviews.models import Review
from glamazer.settings import HOURS, CURRENCY


def sign_up(request):
    fee = None
    if request.GET.get("step") == '2':
        if request.method == "POST":

            form = LocationArtistDetails(request.POST)

            if form.is_valid():
                data = form.cleaned_data
                artist = Artist.objects.filter(user=request.user).update(
                    style=int(data['style']),
                    lat=data["lat"],
                    lng=data["lng"],
                    step=0,
                    )
                return HttpResponseRedirect(reverse('artists_profile')+"?show_hint=1")
        else:
            form = LocationArtistDetails()
    else:
        if request.method == "POST":

            request.GET.get("step")
            form = ArtistForm(request.POST)

            if form.is_valid():
                data = form.cleaned_data
                form.save()
                user = authenticate(
                    email=data['email'], password=data['password'])
                artist = Artist.objects.create(user=user)
                ReceiverAccount.objects.create(user=user, paypal_email=user.email)
                WorkTime.objects.create(artist=artist)

                if user is not None and user.is_active:
                        artist.step = 2
                        artist.save()
                        auth_login(request, user)
                        send_email(case=1, receiver=user)
                        return HttpResponseRedirect(reverse('artists_sign_up')+"?step=2")
        else:
            form = ArtistForm()

    return render(request, 'artists/sign_up.html', {'form': form, "fee": fee})


def facebook_registration(request):
    data = request.POST

    password = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(6))

    is_user = get_object_or_None(User, email=data['email'])

    if not is_user:
        username = ''.join(random.choice(string.ascii_lowercase + string.digits)for x in range(16))
        new_user = User.objects.create_user(
            username=username,
            first_name=data['name'],
            email=data['email'],
            password=password,
            related_with="artists"
            )
        artist = Artist.objects.create(user=new_user, facebook_id=data['facebook_id'], step=2)
        ReceiverAccount.objects.create(user=new_user, paypal_email=new_user.email)
        WorkTime.objects.create(artist=artist)

        hash_name = ''.join(random.choice(string.ascii_lowercase + string.digits)for x in range(10))
        path = '/' + MEDIA_FOLDER + '/artists/' + str(artist.id) + '/avatar/' + hash_name + '.jpeg'
        full_path = MEDIA_ROOT + 'artists/' + str(artist.id) + '/avatar/' + hash_name + '.jpeg'
        d = os.path.dirname(full_path)
        if not os.path.exists(d):
            os.makedirs(d)
        else:
            shutil.rmtree(d)
            os.makedirs(d)
        urllib.request.urlretrieve(data['avatar'], full_path)

        artist.avatar = path
        artist.save()
        kwargs = {}
        kwargs['password'] = password
        send_email(case=3, receiver=new_user, **kwargs)

        login_user(request, new_user)
    else:
        raise Exception("Not registered")


def profile(request, artist_id=None, name=None):

    is_sub = False
    is_follower = None
    profiles = []
    user = request.user

    if not artist_id:
        artist = get_object_or_404(Artist, user__id=user.id)
    else:
        artist = get_object_or_404(Artist, id=artist_id)
        try:
            if user.salon:
                if artist.salon == user.salon:
                    is_sub = True
        except:
            is_sub = False

    listings = Listing.objects.filter(artist=artist, status=1)

    if user.is_authenticated():
        is_follower = get_object_or_None(Followers, user=user, artist=artist)

        if request.GET.get('followed', None) == '1' and not is_follower:
                is_follower = Followers.objects.create(artist=artist, user=user)
                start_following(user, artist.user)
        elif request.GET.get('followed', None) == '0' and is_follower:
            follower = Followers.objects.get(artist=artist, user=user)
            follower.delete()
    followers = Followers.objects.select_related().filter(artist=artist)
    followers = list(followers)
    for follower in followers:
        if follower.user.related_with == 'profiles':
            profiles.append(follower.user.profile)
        elif follower.user.related_with == 'artists':
            profiles.append(follower.user.artist)
        else:
            profiles.append(follower.user.salon)

    reviews = Review.objects.filter(artist=artist)
    rate = get_rate(reviews)

    work_time = get_object_or_None(WorkTime, artist=artist)
    return render(request, 'artists/profile.html', {
        'artist': artist,
        'listings': listings,
        'reviews': reviews,
        'rate': rate,
        'is_follower': is_follower,
        'is_sub': is_sub,
        'profiles': profiles,
        'work_time': work_time,
    })


@login_required
def edit(request):

    user = request.user
    artist = user.artist

    if request.method == 'POST':
        form = EditArtist(request.POST, request.FILES, instance=artist)
        if form.is_valid():
            form.save()
            messages.add_message(request, messages.SUCCESS, _("Your profile is updated."))
            return HttpResponseRedirect(reverse('edit_artist_profile'))
    else:
        print(artist.enable_emails)
        form = EditArtist(instance=artist,
                          initial={'name': user.first_name,
                                   'avatar': artist.avatar,
                                   'description': artist.description,
                                   'style': artist.style,
                                   'lat': artist.lat,
                                   'lng': artist.lng,
                                   'mobile_number': artist.mobile_number,
                                   'enable_emails': artist.enable_emails,
                                   'enable_sms': artist.enable_sms})

    return render(request, 'artists/settings/edit.html', {'artist': artist, "form": form})


def upload(request):
    artist = request.user.artist

    if request.method == 'POST':
        fee = get_fee(artist)
        form = UploadListing(request.POST, request=request)
        if form.is_valid():
            listing = form.save(artist, request.POST)
            messages.add_message(request, messages.INFO,
                _("Your listing %s has been successfully created and submitted for review. Your listing will go live within the next couple of hours.") % listing.title)
            return HttpResponseRedirect(reverse('all_listing'))

    else:
        form = UploadListing()
        fee = get_fee(artist)

    return render(request, 'artists/upload.html', {'artist': artist, "form": form, "fee": fee})


def all_listings(request):
    artist = request.user.artist
    listings = Listing.objects.filter(artist=artist)
    if request.method == "POST" and request.POST.get("id", None):
        listing_id = int(request.POST.get("id", None))
        listing = Listing.objects.get(id=listing_id)
        listing.delete()
    return render(request, 'artists/management/listings.html', {'listings': listings})


def bookings(request):
    user = request.user
    artist = Artist.objects.get(user=user)
    bookings = Booking.objects.select_related().filter(artist=artist)

    if request.method == 'POST':
        sn = request.POST.get('sn', None)
        sn_approve = request.POST.get('sn_approve', None)

        if sn:
            b = Booking.objects.get(id=int(sn))
            if b.status == 0:
                decline_booking_request, cancel_booking_request(artist.user, b.client.user, b.listing)
            else:
                cancel_booking_request(artist.user, b.client.user, b.listing)
            b.status = 2
            b.cancelled_by = 1
            b.save()
            void_authorization(b.id)

        elif sn_approve:
            b = Booking.objects.get(id=int(sn_approve))
            accept_booking_request(artist.user, b.client.user, b.listing)
            b.status = 1
            b.cancelled_by = 1
            b.save()

        return redirect(reverse("artists_bookings"))

    bookings = paginator(request, bookings, 10)
    return render(request, 'artists/bookings.html', {"bookings": bookings})


def account(request):
    return render(request, 'artists/settings/account.html', {"user": request.user})


def schedule(request):
    artist = request.user.artist
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
    return render(request, 'artists/management/schedule.html', {"work_time": work_time})


def calendar(request):
    if request.method == "POST":
        start_time = request.POST.get("start_time", None)
        end_time = request.POST.get("end_time", None)
        comment = request.POST.get("comment", None)
        if start_time and end_time:
            Busy.objects.create(
                artist=request.user.artist,
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
    artist = get_object_or_404(Artist, user=request.user)
    bookings = Booking.objects.select_related().filter(artist=artist, status__in=[0, 1])
    busy = Busy.objects.filter(artist=artist)
    return render(request, 'artists/management/calendar.html', {"artist": artist, "bookings": bookings, "busy": busy})


def cancellation_policy(request):
    user = request.user
    artist = Artist.objects.get(user=user)
    if request.method == "POST":
        data = int(request.POST.get("cancel_id", None))
        if data == -1:
            percent = request.POST.get("percent", None)
            days = request.POST.get("days", None)
            cp = CancellationPolicy.objects.filter(days_before=int(days), percent=int(percent))
            check_if_in_use = ArtistPolicy.objects.filter(status__in=[1, 2], cancellation_policy__in=cp)
            if cp and check_if_in_use:
                cp_id = int(cp[0]['id'])
                ArtistPolicy.objects.filter(artist=artist, status=1).update(status=2)
                ArtistPolicy.objects.create(artist=artist, cancellation_policy_id=cp_id, status=1)
                messages.add_message(request, messages.SUCCESS,
                     _("Your cancellation policy have been changed."))
            else:
                cp = CancellationPolicy.objects.create(days_before=int(days), percent=int(percent))
                ArtistPolicy.objects.create(artist=artist, cancellation_policy=cp, status=0)
                messages.add_message(request, messages.INFO,
                     _("Your request have been submited. We'll review your new policy and will get back to you in the next 2 hours."))
        else:
            ArtistPolicy.objects.filter(artist=artist, status=1).update(status=2)
            ArtistPolicy.objects.create(artist=artist, cancellation_policy_id=data, status=1)
            messages.add_message(request, messages.SUCCESS,
                 _("Your cancellation policy have been changed."))

        return HttpResponseRedirect(reverse('artist_cancellation_policy'))

    artist_policy = ArtistPolicy.objects.select_related("cancellationpolicy").filter(artist=artist, status__in=[1, 2])
    current_id = [x.cancellation_policy_id for x in artist_policy if x.status == 1][0]
    artist_policy = [x.cancellation_policy for x in artist_policy if x.cancellation_policy_id not in range(5)]

    return render(request, 'artists/settings/cancellation_policy.html', {"cp": artist_policy, "current_id": current_id})


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

    return render(request, 'artists/settings/payments.html', {"ra": ra})


def wallet(request):
    ''''''
    transactions, all_earnings, all_widthraws, avaible_funds = [], 0, 0, 0
    user = request.user
    artist = user.artist
    transactions = Withdraw.objects.filter(user=user)

    avaible_funds = artist.money
    currency = dict(CURRENCY)[artist.currency]

    for t in transactions:
        all_widthraws += t.money

    all_earnings = all_widthraws + artist.money
    return render(request, 'artists/wallet.html', {
                                                 "transactions": transactions,
                                                 "all_earnings": all_earnings,
                                                 "all_widthraws": all_widthraws,
                                                 "avaible_funds": avaible_funds,
                                                 "currency": currency,
                                                 })


def withdraw(request):
    if request.method == "POST":
        amount = request.POST.get("amount", None)
        user = request.user
        artist = user.artist
        if not(amount and amount.isdigit() and artist.money >= int(amount) and int(amount) >= MIN_WITHDRAW):
            messages.add_message(request, messages.ERROR,
                 _("Please enter a valid amount."))
            return redirect(reverse("artists_withdraw"))
        else:
            artist.money = artist.money-int(amount)
            artist.save()
            option = ReceiverAccount.objects.filter(user=user)[0]
            Withdraw.objects.create(
                user=user,
                option=option,
                money=round(float(amount), 2),
                method=option.method
                )
            return redirect(reverse("artists_wallet"))

    user = request.user
    artist = user.artist
    if artist.money < MIN_WITHDRAW:
        messages.add_message(request, messages.ERROR,
             _("You need to earn at least $30 to proceed with the withdrawal request."))
        return redirect(reverse("artists_wallet"))

    money = artist.money

    return render(request, 'artists/withdraw.html', {"money": money})


def get_chart_info(request):
    ''' lvc is a reference for listing view count'''
    ''' abc is a reference for all booking count'''
    ''' sbc is a reference for good booking count'''
    if request.method == 'GET':
        lvc, abc, sbc = [], [], []
        data = request.GET.getlist('interval[]')
        artist = request.user.artist
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


def salon_apply(request, salon_id):
    artist = request.user.artist
    artist.salon_id = salon_id
    artist.waiting_for_hired = True
    artist.save()
    messages.add_message(request, messages.SUCCESS, _("Your membership request has been sent to the salon."))
    apply_for_salon(artist.user, artist.salon.user)
    return redirect(reverse("profile_salon", kwargs={"salon_id": salon_id, "name": " "}))


def salon_suspend(request, salon_id):
    artist = request.user.artist
    artist.salon_id = salon_id
    artist.waiting_for_fired = True
    artist.save()
    messages.add_message(request, messages.SUCCESS, _("Your request for suspend from the salon was sent."))
    suspend_from_salon(artist.user, artist.salon.user)
    return redirect(reverse("profile_salon", kwargs={"salon_id": salon_id, "name": " "}))
