import string
import random

from django.template.loader import render_to_string

from glamazer.settings import SUBJECTS
from glamazer.users.models import ConfirmationToken, PasswordToken
from glamazer.core.helpers import get_object_or_None, send_email
from glamazer.notifications.models import Notification
from glamazer.core.helpers import get_twilio
from glamazer.followers.models import Followers
from glamazer.settings import NOTIFICATIONS_LONG, NOTIFICATIONS_SHORT, SMS, TWILIO_NUMBER


def welcome(sender, receiver, password=None, event=None):
    '''Welcome messages'''
    subject = SUBJECTS[0]
    name = receiver.first_name
    to = receiver.email
    if event == 'facebook':
        html_content = render_to_string('emails/facebook_welcome.html', {'receiver_name': name, 'password': password})
    else:
        emails_templates = {
            'profiles': 'emails/1.html',
            'artists': 'emails/artist_welcome.html',
            'salons': 'emails/salon_welcome.html',
        }
        html_content = render_to_string(emails_templates[receiver.related_with], {'receiver_name': name})
    send_email(subject, html_content, to)


def new_artist_to_salon(sender, receiver, password):
    salon_name = sender.first_name
    name = receiver.first_name
    to = receiver.email
    subject = SUBJECTS[15].format(salon_name=salon_name)
    html_content = render_to_string("emails/artist_welcome_from_salon.html", {'name': name, 'salon_name': salon_name, 'password': password})
    send_email(subject, html_content, to)


def forgotten_password(sender, receiver):
    '''Forgotten Password'''
    subject = SUBJECTS[1]
    name = receiver.first_name
    to = receiver.email
    email_token = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(32))
    token = get_object_or_None(PasswordToken, email=receiver.email)
    if token:
            token.email_token = email_token
            token.save()
    else:
            PasswordToken.objects.create(email=receiver.email, email_token=email_token)
    link = 'http://glamfame.com/users/change_password/{0}'.format(email_token)
    html_content = render_to_string('emails/password.html', {'receiver_name': name, 'link': link})
    send_email(subject, html_content, to)


def send_booking_request(sender, receiver, listing):
    data = {
        "id": sender.profile.id,
        "name": sender.first_name,
        "listing_id": listing.id,
        "title": listing.title,
    }
    Notification.objects.create(
        sender=sender,
        receiver=receiver,
        short_text=NOTIFICATIONS_SHORT[0].format(**data),
        long_text=NOTIFICATIONS_LONG[0].format(**data),
    )
    # SMS
    artist = receiver.artist
    mobile = artist.mobile_number
    if artist.enable_sms and mobile and mobile[0] == '+':
        client = get_twilio()
        client.messages.create(
            to=mobile,
            from_=TWILIO_NUMBER,
            body=SMS[0].format(**data),
        )


def accept_booking_request(sender, receiver, listing):
    data = {
        "id": sender.artist.id,
        "name": sender.first_name,
        "listing_id": listing.id,
        "title": listing.title,
    }
    Notification.objects.create(
        sender=sender,
        receiver=receiver,
        short_text=NOTIFICATIONS_SHORT[1].format(**data),
        long_text=NOTIFICATIONS_LONG[1].format(**data),
    )
    # SMS
    profile = receiver.profile
    mobile = profile.mobile_number
    if profile.enable_sms and mobile and mobile[0] == '+':
        client = get_twilio()
        client.messages.create(
            to=mobile,
            from_=TWILIO_NUMBER,
            body=SMS[1].format(**data),
        )


def decline_booking_request(sender, receiver, listing):
    data = {
        "id": sender.artist.id,
        "name": sender.first_name,
        "listing_id": listing.id,
        "title": listing.title,
    }
    Notification.objects.create(
        sender=sender,
        receiver=receiver,
        short_text=NOTIFICATIONS_SHORT[2].format(**data),
        long_text=NOTIFICATIONS_LONG[2].format(**data),
    )
    # SMS
    profile = receiver.profile
    mobile = profile.mobile_number
    if profile.enable_sms and mobile and mobile[0] == '+':
        client = get_twilio()
        client.messages.create(
            to=mobile,
            from_=TWILIO_NUMBER,
            body=SMS[2].format(**data),
        )


def cancel_booking_request(sender, receiver, listing):
    '''Bad news! <a href="/artists/profile/{id}">{name}</a> cancelled your appointment for <a href="/listings/{listing_id}">{title}</a>. Your money will be refunded in 24 hours. As a little compensation from our side, your next booking will be with 5% discount from the regular price.'''
    '''We are sorry to bring bad news! <a href="/users/profile/{id}">{name}</a> cancelled the appointment for <a href="/listings/{listing_id}">{title}</a>.  As a compensation, in 24 hours you will receive 50% of the price of the booking.'''
    if sender.related_with == 'artists':
        data = {
            "id": sender.artist.id,
            "name": sender.first_name,
            "listing_id": listing.id,
            "title": listing.title,
        }
        Notification.objects.create(
            sender=sender,
            receiver=receiver,
            short_text=NOTIFICATIONS_SHORT[3].format(**data),
            long_text=NOTIFICATIONS_LONG[3].format(**data),
        )
        # SMS
        profile = receiver.profile
        mobile = profile.mobile_number
        if profile.enable_sms and mobile and mobile[0] == '+':
            client = get_twilio()
            client.messages.create(
                to=mobile,
                from_=TWILIO_NUMBER,
                body=SMS[3].format(**data),
            )

    elif sender.related_with == 'profiles':
        data = {
            "id": sender.profile.id,
            "name": sender.first_name,
            "listing_id": listing.id,
            "title": listing.title,
        }
        Notification.objects.create(
            sender=sender,
            receiver=receiver,
            short_text=NOTIFICATIONS_SHORT[4].format(**data),
            long_text=NOTIFICATIONS_LONG[4].format(**data),
        )
        # SMS
        artist = receiver.artist
        mobile = artist.mobile_number
        if artist.enable_sms and mobile and mobile[0] == '+':
            client = get_twilio()
            client.messages.create(
                to=mobile,
                from_=TWILIO_NUMBER,
                body=SMS[4].format(**data),
            )


def transfer_money(sender, receiver, amount):
    pass


def start_following(sender, receiver):
    '''On start following'''
    data = {
        "id": 0,
        "type": "",
        "name": sender.first_name,
    }
    if sender.related_with == 'profiles':
        data["id"] = sender.profile.id
        data["type"] = "users"
    elif sender.related_with == 'artists':
        data["id"] = sender.artist.id
        data["type"] = "artists"
    else:
        data["id"] = sender.salon.id
        data["type"] = "artists"

    Notification.objects.create(
        sender=sender,
        receiver=receiver,
        short_text=NOTIFICATIONS_SHORT[6].format(**data),
        long_text=NOTIFICATIONS_LONG[6].format(**data),
    )

    '''
        After the artist have new follower
        5 - independent artist
        6 - not independant artist
    '''
    to = receiver.email
    artist = receiver.artist
    address = 'emails/5.html' if artist.salon else 'emails/6.html'
    username = sender.first_name
    subject = SUBJECTS[5].format(username=username)
    count = Followers.objects.filter(artist=artist).count()
    link = 'http://glamfame.com/artists/profile/{0}'.format(artist.id)
    artistname = receiver.first_name
    receiver_name = receiver.first_name
    html_content = render_to_string(address, {'receiver_name': receiver_name, 'username': username, 'artistname': artistname, 'count': count, 'link': link})
    send_email(subject, html_content, to)


def add_to_wishlist(sender, receiver, listing):
    data = {
        "id": sender.profile.id,
        "type": "users",
        "name": sender.first_name,
        "listing_id": listing.id,
        "title": listing.title,
    }

    Notification.objects.create(
        sender=sender,
        receiver=receiver,
        short_text=NOTIFICATIONS_SHORT[7].format(**data),
        long_text=NOTIFICATIONS_LONG[7].format(**data),
    )


def user_review(sender, receiver, listing):
    data = {
        "id": sender.profile.id,
        "name": sender.first_name,
        "listing_id": listing.id,
        "title": listing.title,
    }
    Notification.objects.create(
        sender=sender,
        receiver=receiver,
        short_text=NOTIFICATIONS_SHORT[8].format(**data),
        long_text=NOTIFICATIONS_LONG[8].format(**data),
    )


def new_listing(sender, receiver, listing):
    data = {
        "id": sender.artist.id,
        "name": sender.first_name,
        "listing_id": listing.id,
        "title": listing.title,
    }
    followers = Followers.objects.select_related().filter(artist=sender.artist)
    for follower in followers:
        Notification.objects.create(
            sender=sender,
            receiver_id=follower.user_id,
            short_text=NOTIFICATIONS_SHORT[9].format(**data),
            long_text=NOTIFICATIONS_LONG[9].format(**data),
        )


def approved_listing(sender, receiver, listing):
    data = {
        "type": receiver.related_with,
        "listing_id": listing.id,
    }
    Notification.objects.create(
        sender_id=1,
        receiver=receiver,
        short_text=NOTIFICATIONS_SHORT[10].format(**data),
        long_text=NOTIFICATIONS_LONG[10].format(**data),
    )


def bad_listing(sender, receiver, listing):
    data = {
        "type": receiver.related_with,
        "listing_id": listing.id,
    }
    Notification.objects.create(
        sender_id=1,
        receiver=receiver,
        short_text=NOTIFICATIONS_SHORT[11].format(**data),
        long_text=NOTIFICATIONS_LONG[11].format(**data),
    )


def apply_for_salon(sender, receiver):
    Notification.objects.create(
        sender=sender,
        receiver=receiver,
        short_text=NOTIFICATIONS_SHORT[12].format(name=sender.first_name),
        long_text=NOTIFICATIONS_LONG[12].format(name=sender.first_name),
    )


def suspend_from_salon(sender, receiver):
    Notification.objects.create(
        sender=sender,
        receiver=receiver,
        short_text=NOTIFICATIONS_SHORT[13].format(name=sender.first_name),
        long_text=NOTIFICATIONS_LONG[13].format(name=sender.first_name),
    )


def accept_work_request(sender, receiver):
    Notification.objects.create(
        sender=sender,
        receiver=receiver,
        short_text=NOTIFICATIONS_SHORT[14].format(name=sender.first_name),
        long_text=NOTIFICATIONS_LONG[14].format(name=sender.first_name),
    )


def reject_work_request(sender, receiver):
    Notification.objects.create(
        sender=sender,
        receiver=receiver,
        short_text=NOTIFICATIONS_SHORT[15].format(name=sender.first_name),
        long_text=NOTIFICATIONS_LONG[15].format(name=sender.first_name),
    )


def accept_suspend_request(sender, receiver):
    Notification.objects.create(
        sender=sender,
        receiver=receiver,
        short_text=NOTIFICATIONS_SHORT[16],
        long_text=NOTIFICATIONS_LONG[16],
    )


def reject_suspend_request(sender, receiver):
    Notification.objects.create(
        sender=sender,
        receiver=receiver,
        short_text=NOTIFICATIONS_SHORT[17],
        long_text=NOTIFICATIONS_LONG[17],
    )
