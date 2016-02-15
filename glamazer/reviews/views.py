from django.shortcuts import render, redirect, get_object_or_404

from glamazer.core.notifications import user_review
from glamazer.reviews.models import WaitingForFeedback, Review
from glamazer.core.helpers import login_user


def receive_review(request, email_token):
    token = get_object_or_404(WaitingForFeedback, token=email_token)

    if request.method == 'POST':
        data = request.POST
        text = data['text']
        rate = data['rate']
        r = Review.objects.create(
            client_id=token.client_id,
            artist_id=token.artist_id,
            listing_id=token.listing_id,
            booking_id=token.booking_id,
            rating=rate,
            text=text
            )
        r.save()
        user_review(token.client.user, token.artist, token.listing)
        listing = token.listing
        listing.comments = int(listing.comments) + 1
        listing.save()

        token.delete()
        return redirect("/")

    profile = token.client
    # token.delete()
    artist = token.artist
    login_user(request, profile.user)

    return render(request, 'review/receive.html', {'artist': artist})
