import string
import random
import os
import shutil
import urllib.request

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.utils import simplejson
from django.utils.translation import ugettext as _
from django.contrib import messages
from django.contrib.auth import logout, authenticate
from django.contrib.auth import login as auth_login
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.mail import EmailMultiAlternatives

from glamazer.settings import MEDIA_ROOT, MEDIA_FOLDER
from glamazer.users.forms import ProfileForm, LoginUserForm, ForgottenPasswordForm, ChangePasswordForm, EditProfile
from glamazer.users.models import ConfirmationToken, Profile, PasswordToken
from glamazer.core.helpers import login_user, get_object_or_None, paginator, void_authorization, partially_capture
from glamazer.core.notifications import cancel_booking_request, welcome
from glamazer.listings.models import Listing
from glamazer.favorites.models import Favorite
from glamazer.followers.models import Followers
from glamazer.booking.models import Booking, DummyBooking, ReportedProblems
from glamazer.reviews.models import Review


def sign_up(request):
    request.session.flush()
    if request.method == "POST":

        user_form = ProfileForm(request.POST)

        if user_form.is_valid():
            profile = user_form.save()
            data = user_form.cleaned_data
            user = authenticate(
                email=data['email'], password=data['password'])

            if user is not None and user.is_active:
                login_user(request, profile.user)
                return redirect(reverse("user_profile")+"?show_hint=1")
                # send_email(case=0, receiver=user)
                # messages.add_message(request, messages.INFO,
                #                      'Registration complete. Please check your e-mail to activate your account.')
    else:
        user_form = ProfileForm()

    return render(request, 'user/sign_up.html', {'user_form': user_form})


def login(request):
    if request.method == "POST":

        user_form = LoginUserForm(request.POST)

        if user_form.is_valid():
            data = user_form.cleaned_data
            user = authenticate(
                email=data['email'], password=data['password'])

            if user is not None:
                auth_login(request, user)
                return redirect("/")
    else:
        user_form = LoginUserForm()

    return render(request, 'user/login.html', {'user_form': user_form})


def logout_user(request):
    logout(request)
    return redirect('/')


def forgotten_password(request):
    if request.method == 'POST':
        form = ForgottenPasswordForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            email = data.get('email', None)

            user = get_object_or_None(User, email=email)
            if user:
                welcome(None, user)

            return HttpResponseRedirect(reverse('home'))
    else:
        form = ForgottenPasswordForm()

    return render(request, 'user/forgotten_password.html', {'form': form})


def change_password(request, email_token):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            new_password = data.get('new_password', None)

            email_token = request.POST.get("token", None)
            token = get_object_or_404(PasswordToken, email_token=email_token)

            if token is not None:
                user = User.objects.get(email=token.email)
                user.set_password(new_password)
                user.save()

                user = authenticate(email=token.email, password=new_password)

                token.delete()

            return HttpResponseRedirect(reverse('home'))

    else:
        form = ChangePasswordForm()

    return render(request, 'user/change_password.html', {'form': form, "email_token": email_token})


def confirmation(request, email_token):
    token = get_object_or_404(ConfirmationToken, email_token=email_token)

    if token:
        profile = token.user.profile

        if not profile.is_activated:
            profile.is_activated = True
            profile.save()
            token.delete()
            login_user(request, profile.user)
            return HttpResponseRedirect(reverse('user_settings'))

    return HttpResponseRedirect(reverse('home'))


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
                                            related_with="profiles")
        profile = Profile.objects.create(user=new_user, facebook_id=data['facebook_id'], is_activated=True)

        hash_name = ''.join(random.choice(string.ascii_lowercase + string.digits)for x in range(10))
        path = '/' + MEDIA_FOLDER + '/users/' + str(profile.id) + '/avatar/' + hash_name + '.jpeg'
        full_path = MEDIA_ROOT + 'users/' + str(profile.id) + '/avatar/' + hash_name + '.jpeg'
        d = os.path.dirname(full_path)
        if not os.path.exists(d):
            os.makedirs(d)
        else:
            shutil.rmtree(d)
            os.makedirs(d)
        urllib.request.urlretrieve(data['avatar'], full_path)

        profile.avatar = path
        profile.save()
        kwargs = {}
        kwargs['password'] = password
        welcome(None, new_user, password)

        login_user(request, new_user)
    else:
        raise Exception("Not registered")


def facebook_login(request):
    data = request.POST
    is_user = get_object_or_None(User, email=data['email'])
    if is_user:
        if is_user.first_name == "anonymous":
            is_user.first_name = data['name']
            is_user.facebook_id = data['facebook_id']
            is_user.save()
            profile = is_user.profile
            hash_name = ''.join(random.choice(string.ascii_lowercase + string.digits)for x in range(10))
            path = '/' + MEDIA_FOLDER + '/users/' + str(profile.id) + '/avatar/' + hash_name + '.jpeg'
            full_path = MEDIA_ROOT + 'users/' + str(profile.id) + '/avatar/' + hash_name + '.jpeg'
            d = os.path.dirname(full_path)
            if not os.path.exists(d):
                os.makedirs(d)
            else:
                shutil.rmtree(d)
                os.makedirs(d)
            urllib.request.urlretrieve(data['avatar'], full_path)
            profile.avatar = path
            profile.save()
            login_user(request, is_user)
        else:
            login_user(request, is_user)

        return HttpResponse(simplejson.dumps("COMPLETE"), content_type="application/json")
    else:
        raise Exception("Not registered")


def wishlist(request):
    user = request.user
    favorites = Favorite.objects.select_related().filter(user=user)
    listings = []

    for favorite in favorites:
        listings.append(favorite.listing)

    return render(request, 'listings/listings.html', {'listings': listings, 'title': 'Wishlist'})


def followed(request):
    user = request.user
    followers = Followers.objects.filter(user=user)
    listings_array = []
    listings = []

    for follower in followers:
        artist = follower.artist
        listings_array = Listing.objects.filter(artist=artist)
        for listing in listings_array:
            listings.append(listing)

    return render(request, 'listings/listings.html', {'listings': listings, 'title': 'FOLLOWED ARTISTS'})


def profile(request, user_id=None, name=None):

    if not user_id:
        user = request.user
        profile = get_object_or_404(Profile, user__id=user.id)
    else:
        profile = get_object_or_404(Profile, id=user_id)
        user = profile.user

    listings = []
    artists = []

    favorites = Favorite.objects.select_related("listing").filter(user=user)
    for favorite in favorites:
        listings.append(favorite.listing)

    followers = Followers.objects.select_related("artist").filter(user=user)

    for follower in followers:
        artists.append(follower.artist)

    reviews = Review.objects.filter(client=profile)

    return render(request, 'user/profile.html', {'profile': profile,
                                                 'reviews': reviews,
                                                 'listings': listings,
                                                 'artists': artists})


def settings(request):
    user = request.user
    profile = get_object_or_None(Profile, user=user)

    if request.method == 'POST':
        form = EditProfile(request.POST, request.FILES, instance=profile)

        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('user_settings'))
    else:
        form = EditProfile(instance=profile,
                           initial={'name': user.first_name,
                                    'avatar': profile.avatar,
                                    'enable_emails': profile.enable_emails,
                                    'enable_sms': profile.enable_sms})

    return render(request, 'user/settings.html', {'profile': profile, 'form': form})


def bookings(request):
    user = request.user
    if request.method == 'POST':
        sn = request.POST.get('sn', None)
        is_sanction = request.POST.get('cancellation_policy', None)
        b = Booking.objects.get(id=int(sn))
        if sn and not is_sanction:
            cancel_booking_request(user, b.artist.user, b.listing)
            void_authorization(b.id)
        elif sn and is_sanction:
            partially_capture(b.id)
            cancel_booking_request(user, b.artist.user, b.listing)

        b.status = 2
        b.cancelled_by = 2
        b.save()

        return redirect(reverse("profiles_bookings"))

    profile = Profile.objects.select_related().get(user_id=user.id)
    temp_bookings = Booking.objects.select_related().filter(client=profile).order_by('-start_time')
    bookings = []
    for t in temp_bookings:
        booking = {}
        booking["id"] = t.id
        booking["title"] = t.title
        booking["listing_id"] = t.listing_id
        booking["artist_id"] = t.artist_id
        booking["artist_avatar"] = t.artist.get_avatar()
        booking["artist_name"] = t.artist.user.first_name
        booking["price"] = t.price
        booking["currency"] = t.artist.currency
        booking["status"] = t.get_status_display()
        booking["start_time"] = t.start_time
        booking["listing"] = t.listing.get_picture()
        booking["days_before"] = t.cancellation_policy.days_before
        booking["percent"] = t.cancellation_policy.percent
        booking["dialog"] = 1 if t.status == 1 else 0
        bookings.append(booking)

    bookings = paginator(request, bookings, 10)
    return render(request, 'user/bookings.html', {"bookings": bookings})


def cancel(request):
    if request.method == 'GET':
        dummy_booking = DummyBooking.objects.get(id=int(request.GET.get('sn')))
        dummy_booking.delete()
    return HttpResponse(simplejson.dumps("COMPLETE"), content_type="application/json")


def change_email(request):
    if request.method == 'POST':
        user = request.user
        email = request.POST.get("email", None)
        if email:
            if email == user.email:
                messages.add_message(request, messages.SUCCESS, _('Your email has been changed.'))

            else:
                check_email = User.objects.filter(email=email)
                if check_email:
                    messages.add_message(request, messages.ERROR, _('This email is already taken.'))
                else:
                    user.email = email
                    user.save()
                    messages.add_message(request, messages.SUCCESS, _('Your email has been changed.'))
        else:
                messages.add_message(request, messages.ERROR, _('Opss... Something went wrong.'))

        if user.related_with == "artists":
            return redirect(reverse("edit_artist_account"))
        elif user.related_with == "salons":
            return redirect(reverse("edit_salons_account"))
        else:
            return redirect(reverse("edit_salon_account"))


def change_password_user(request):
    if request.method == 'POST':
        user = request.user
        old_pass = request.POST.get("old_pass", None)
        pass_1 = request.POST.get("new_pass_1", None)
        pass_2 = request.POST.get("new_pass_2", None)
        if user.check_password(old_pass):
            if pass_1 == pass_2:
                if pass_1 == "":
                    messages.add_message(request, messages.ERROR, _("Please enter valid password"))
                else:
                    user.set_password(pass_1)
                    user.save()
                    messages.add_message(request, messages.SUCCESS, _('Your password has been changed.'))
            else:
                messages.add_message(request, messages.ERROR, _('The password should be the same.'))
        else:
            messages.add_message(request, messages.ERROR, _('Please enter correct password.'))

        if user.related_with == "artists":
            return redirect(reverse("edit_artist_account"))
        elif user.related_with == "salons":
            return redirect(reverse("edit_salons_account"))
        else:
            return redirect(reverse("edit_salon_account"))


def report_problem(request):
    sn = request.POST.get("sn", None)
    comment = request.POST.get("comment")
    if sn:
        sn = int(sn)
    else:
        raise Http404

    Booking.objects.filter(id=sn).update(status=4)
    booking = Booking.objects.get(id=sn)
    user_type = request.user.related_with
    ReportedProblems.objects.create(artist=booking.artist,
                                    client=booking.client,
                                    listing=booking.listing,
                                    booking_id=booking.id,
                                    comment=comment,
                                    sender=user_type)

    return redirect(reverse(user_type + "_bookings"))


def send_feedback(request):
    if request.method == "POST":
        try:
            data = request.POST
            name = data.get("name", None)
            from_email = data.get("email", None)
            subject = '[feedback]' + str(data.get("reason", None))
            html_content = 'Name: ' + str(name) + "\n Message: " + data.get("message", None)

            to = 'team@glamfame.com'
            msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
            msg.content_subtype = "html"
            msg.send()
        except:
            pass
        finally:
            messages.add_message(request, messages.ERROR,
                _("Thank you for your feedback. Your opinion is important for us !"))

    return redirect(reverse("about_us"))
