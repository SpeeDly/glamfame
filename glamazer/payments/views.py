import paypalrestsdk
from pymill import pymill

from django.http import Http404
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect

from glamazer.booking.models import Booking, DummyBooking
from glamazer.payments.models import Payment
from glamazer.core.helpers import get_object_or_None, get_UTC_timestamp
from glamazer.core.notifications import send_booking_request
from glamazer.settings import PAYPAL_MODE, PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET, PR_PAYMILL_API_KEY


def start_payment(request):
    sn = request.session.get('dummy_booking_id', None)
    dummy_booking = get_object_or_None(DummyBooking, id=int(sn))
    
    paypalrestsdk.configure({
        'mode': PAYPAL_MODE,
        'client_id': PAYPAL_CLIENT_ID,
        'client_secret': PAYPAL_CLIENT_SECRET
    })

    payment = paypalrestsdk.Payment({
            "intent": "authorize",
            "payer": {
                "payment_method": "paypal"
            },
            "redirect_urls": {
                "return_url": "http://glamfame.com/success",
                "cancel_url": "http://glamfame.com/error"
            },
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": dummy_booking.title,
                        "price": int(dummy_booking.price),
                        "currency": dummy_booking.currency,
                        "quantity": 1
                    }]
                },
                "amount": {
                    "total": int(dummy_booking.price),
                    "currency": "USD"
                },
                "description": dummy_booking.title
            }]
        })

    if not payment.create():
        raise Http404

    request.session['Payment_id'] = payment['id']
    request.session['comment'] = request.POST.get("comment", None)
    _redirect = payment['links'][1]['href'] + "&no_shipping=1"

    return redirect(_redirect)


def success_payment(request):
    '''
     Function for active the authorization with Paypal after the client is successfully redirected from Paypal to our platform
     Or to execute Pymill authorization credit card after successfull bridge on the frontend
    '''
    sn = request.session.get('dummy_booking_id', None)
    if sn:
        dummy_booking = DummyBooking.objects.get(id=int(sn))
    else:
        return redirect(reverse("error"))

    request.session['dummy_booking_id'] = ''

    # get required arguments
    payer_id = request.GET.get('PayerID', None)
    payment_id = request.session.get('Payment_id', None)
    token = request.POST.get("token", None)
    print(request.POST, request.GET)

    if request.POST.get("comment", None):
        comment = request.POST.get("comment", None)
    else:
        comment = request.session.get('comment', None)

    if payer_id and payment_id:
        # empty the garbage
        request.session['Payment_id'] = ''

        # authorize paypal account
        paypalrestsdk.configure({
            'mode': PAYPAL_MODE,
            'client_id': PAYPAL_CLIENT_ID,
            'client_secret': PAYPAL_CLIENT_SECRET
        })
        # execute the authorization
        payment = paypalrestsdk.Payment.find(payment_id)
        payment.execute({"payer_id": payer_id})
        # serialize the data
        data = payment['transactions'][0]['related_resources'][0]['authorization']
        state = data['state']
        create_time = get_UTC_timestamp(data['create_time'])
        valid_until = get_UTC_timestamp(data['valid_until'])
        price = data["amount"]["total"]
        currency = data["amount"]["currency"]
        payer_id = payment["payer"]["payer_info"]["payer_id"]
        payment_id = payment["id"]
        authorization_id = data["id"]
        transaction_id = data["id"]
        payment_method = 1
    elif token:
        price = int(dummy_booking.price)*100
        description = "{0}-{1}".format(dummy_booking.listing_id, dummy_booking.title)
        p = pymill.Pymill(PR_PAYMILL_API_KEY)
        preauth = p.preauthorize(
            amount=price,
            currency=dummy_booking.currency,
            description=description,
            token=token
        )

        # serialize the data
        data = preauth.preauthorization
        state = data["status"]
        create_time = int(data['created_at'])
        valid_until = create_time + 604800  # 7days * 24hours * 60min * 60 secs = 604800
        price = int(data["amount"])/100
        currency = data["currency"]
        payer_id = data["client"]["id"]
        payment_id = data["payment"]["id"]
        authorization_id = data["id"]
        transaction_id = preauth.id
        payment_method = 2
    else:
        return redirect(reverse("error"))

    # if everything is OK, create real copy of the dummy booking
    booking = Booking.objects.create(
        artist=dummy_booking.artist,
        listing=dummy_booking.listing,
        client=dummy_booking.client,
        cancellation_policy=dummy_booking.cancellation_policy,
        revenue=dummy_booking.revenue,
        price=dummy_booking.price,
        title=dummy_booking.title,
        start_time=dummy_booking.start_time,
        end_time=dummy_booking.end_time,
        status=0,
        comment=comment,
    )
    send_booking_request(dummy_booking.client.user, dummy_booking.artist.user, dummy_booking.listing)
    # and destroy the old one
    dummy_booking.delete()

    Payment.objects.create(
        booking_id=booking.id,
        payment_method=payment_method,
        state=state,
        create_time=create_time,
        valid_until=valid_until,
        price=booking.price,
        currency=currency,
        payer_id=payer_id,
        payment_id=payment_id,
        authorization_id=authorization_id,
        transaction_id=transaction_id,
        )

    return render(request, 'payments/success.html', {})


def error_payment(request):
    ''' Delete everything what we can find about this booking '''
    sn = request.session.get('dummy_booking_id', None)
    listing_id = 0
    if sn:
        dummy_booking = DummyBooking.objects.get(id=int(sn))
        listing_id = dummy_booking.listing_id
        dummy_booking.delete()
    request.session['dummy_booking_id'] = ''
    request.session['Payment_id'] = ''

    return redirect("/listings/{0}".format(listing_id))


def cancel_payment(request):
    ''' Delete everything what we can find about this booking '''
    sn = request.session.get('dummy_booking_id', None)
    if sn:
        dummy_booking = DummyBooking.objects.get(id=int(sn))
        listing_id = dummy_booking.listing_id
        dummy_booking.delete()
    request.session['dummy_booking_id'] = ''
    request.session['Payment_id'] = ''

    return redirect("/listings/{0}".format(listing_id))
