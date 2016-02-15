import string
import random

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from glamazer.settings import SUBJECTS, SENDER
from glamazer.users.models import ConfirmationToken, PasswordToken
from glamazer.core.helpers import get_object_or_None


def send_email(case, receiver, **kwargs):
    # User Welcome message
    to = receiver.email
    from_email = SENDER

    if case == 0:
        subject = SUBJECTS[0]
        receiver_name = receiver.first_name
        email_token = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(32))
        confirmation = ConfirmationToken(user=receiver, email_token=email_token)
        confirmation.save()
        link = 'http://glamfame.com/users/confirmation/{0}'.format(email_token)
        html_content = render_to_string('emails/1.html', {'receiver_name': receiver_name, 'link': link})

    # Artist Welcome Message
    elif case == 1:
        subject = SUBJECTS[0]
        receiver_name = receiver.first_name
        html_content = render_to_string('emails/artist_welcome.html', {'receiver_name': receiver_name})

    # Salon Welcome Message
    elif case == 2:
        subject = SUBJECTS[0]
        receiver_name = receiver.first_name
        html_content = render_to_string('emails/salon_welcome.html', {'receiver_name': receiver_name})

    # Facebook welcome message
    elif case == 3:
        subject = SUBJECTS[0]
        receiver_name = receiver.first_name
        html_content = render_to_string('emails/facebook_welcome.html', {'receiver_name': receiver_name, 'password': kwargs['password']})

    # Forgotten Password
    elif case == 4:
        subject = SUBJECTS[1]
        receiver_name = receiver.first_name
        email_token = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(32))
        token = get_object_or_None(PasswordToken, email=receiver.email)
        if token:
                token.email_token = email_token
                token.save()
        else:
                PasswordToken.objects.create(email=receiver.email, email_token=email_token)
        link = 'http://glamfame.com/users/change_password/{0}'.format(email_token)
        html_content = render_to_string('emails/password.html', {'receiver_name': receiver_name, 'link': link})

    # After the artist have new follower
    elif case == 8:
        receiver_name = receiver.first_name
        username = kwargs.pop('username', None)
        subject = SUBJECTS[5].format(username=username)
        count = kwargs.pop('count', None)
        link = 'http://glamfame.com/artists/profile/{0}'.format(kwargs.pop('id', None))
        html_content = render_to_string('emails/5.html', {'receiver_name': receiver_name, 'username': username, 'count': count, 'link': link})

    # After the artist have new follower and is assigned to a salon
    elif case == 9:
        receiver_name = receiver.first_name
        username = kwargs.pop('username', None)
        artistname = kwargs.pop('artistname', None)
        subject = SUBJECTS[6].format(username=username, artistname=artistname)
        count = kwargs.pop('count', None)
        link = 'http://glamfame.com/artists/profile/{0}'.format(kwargs.pop('id', None))
        html_content = render_to_string('emails/6.html', {'receiver_name': receiver_name, 'username': username, 'artistname': artistname, 'count': count, 'link': link})

    # Email for artist when he have a new booking request
    elif case == 10:
        receiver_name = receiver.first_name
        listing = kwargs.pop('listing', None)
        username = kwargs.pop('username', None)
        subject = SUBJECTS[7].format(title=listing.title)
        link = 'http://glamfame.com/artists/bookings'
        html_content = render_to_string('emails/7.html', {'receiver_name': receiver_name, 'username': username, 'listing': listing, 'link': link})

    # Email for salon when artist who is assigned to him have a new booking request
    elif case == 11:
        listing = kwargs.pop('listing', None)
        subject = SUBJECTS[7].format(title=listing.title)
        receiver_name = receiver.first_name
        username = kwargs.pop('username', None)
        artistname = kwargs.pop('artistname', None)
        link = 'http://glamfame.com/salons/bookings'
        html_content = render_to_string('emails/8.html', {'receiver_name': receiver_name, 'username': username, 'artistname': artistname, 'listing': listing, 'link': link})

    # When booking request is approved
    elif case == 12:
        subject = SUBJECTS[9]
        receiver_name = receiver.first_name
        listing = kwargs.pop('listing', None)
        artistname = kwargs.pop('artistname', None)
        when = kwargs.pop('when', None)
        html_content = render_to_string('emails/10.html', {'receiver_name': receiver_name, 'artistname': artistname, 'listing': listing, 'when': when})

    # When booking request is rejected
    elif case == 13:
        subject = SUBJECTS[10]
        receiver_name = receiver.first_name
        artistname = kwargs.pop('artistname', None)
        html_content = render_to_string('emails/11.html', {'receiver_name': receiver_name, 'artistname': artistname})

    # When booking request is declined from the client, after it was approved, no charged
    elif case == 14:
        receiver_name = receiver.first_name
        username = kwargs.pop('username', None)
        when = kwargs.pop('when', None)
        subject = SUBJECTS[11].format(when=when)
        day_before = kwargs.pop('day_before', None)
        html_content = render_to_string('emails/12.html', {'receiver_name': receiver_name, 'username': username, 'when': when, 'day_before': day_before})

    # When booking request is declined from the client, after it was approved, with charge
    elif case == 15:
        receiver_name = receiver.first_name
        username = kwargs.pop('username', None)
        when = kwargs.pop('when', None)
        subject = SUBJECTS[11].format(when=when)
        day_before = kwargs.pop('day_before', None)
        html_content = render_to_string('emails/13.html', {'receiver_name': receiver_name, 'username': username, 'when': when, 'day_before': day_before})

    # When booking request is approved from the artist, and cancelled afterthat
    elif case == 16:
        receiver_name = receiver.first_name
        artistname = kwargs.pop('artistname', None)
        when = kwargs.pop('when', None)
        subject = SUBJECTS[11].format(when=when)
        listing_id = kwargs.pop('listing_id', None)
        html_content = render_to_string('emails/14.html', {'receiver_name': receiver_name, 'artistname': artistname, 'when': when, 'listing_id': listing_id})

    # After the book time. Email for feedback !
    elif case == 17:
        receiver_name = receiver.first_name
        artistname = kwargs.pop('artistname', None)
        token = kwargs.pop('token', None)
        subject = SUBJECTS[12]
        link = 'http://glamfame.com/reviews/{0}'.format(token)
        html_content = render_to_string('emails/15.html', {'receiver_name': receiver_name, 'artistname': artistname, 'link': link})

    # When we automatically create an user
    elif case == 18:
        subject = SUBJECTS[0]
        receiver_name = receiver.first_name
        html_content = render_to_string('emails/19.html', {'receiver_name': receiver_name, 'password': kwargs['password']})

    msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
    msg.content_subtype = "html"
    msg.send()
