import os
import string
import random

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "glamazer.settings")

from glamazer.core.helpers import current_time, full_capture
from glamazer.core.emails import send_email
from glamazer.booking.models import Booking
from glamazer.reviews.models import WaitingForFeedback


def send_review_email():

    now = current_time()
    passed_bookings = Booking.objects.select_related().filter(end_time__lt=now, review_email=False, status=1)
    bookings_ids = []
    for b in passed_bookings:
        token = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(32))

        WaitingForFeedback.objects.create(
            client=b.client,
            artist=b.artist,
            listing=b.listing,
            booking=b,
            token=token
            )

        full_capture(b.id)
        bookings_ids.append(b.id)
        kwargs = {}
        kwargs['artistname'] = b.artist.user.first_name
        kwargs['token'] = token
        send_email(case=17, receiver=b.client.user, **kwargs)

    Booking.objects.filter(id__in=bookings_ids).update(status=3, review_email=True)
send_review_email()