import datetime

from haystack.query import SQ, SearchQuerySet
from haystack.utils.geo import Point, D

from django.http import HttpResponse
from django.db import connection
from django.db.models import Avg
from django.utils import simplejson, translation
from django.shortcuts import render

from glamazer.reviews.models import Review
from glamazer.listings.models import Listing, Tags
from glamazer.notifications.models import Hint
from glamazer.core.helpers import dictfetchall
from glamazer.settings import STYLE_INDEXES, MEDIA_ROOT, CURRENCY


def home(request):
    listings = Listing.objects.select_related().filter(status=1).order_by('?')[:20]
    listings = list(listings)
    return render(request, 'core/home.html', {"listings": listings})


def base(request):
    styles = {
        "hairstyle": "hair",
        "nails-design": "nails",
        "make-up": "make up",
    }
    path = styles.get(request.path.strip('/'), None)

    lang = "default" if request.session['django_language'] == "en" else "default_ru"
    _listings = SearchQuerySet().models(Listing).using(lang).filter(style=path, status=1)

    price_list = [l.price for l in _listings]
    try:
        price_list = [min(price_list), max(price_list)]
    except:
        price_list = [0, 500]
    price_list = [min(price_list), max(price_list)]

    listings = []
    listing = {}
    artists_ids = []
    currencies = dict(CURRENCY)
    for l in _listings:
        listing = {
            "lat": l.location.x,
            "lng": l.location.y,
            "id": l.listing_id,
            "picture": l.get_picture,
            "style": l.style,
            "title": l.title,
            "likes": l.likes,
            "price": int(l.price),
            "currency": currencies[l.currency],
            "comments": l.comments,
            "artist_id": l.artist_id,
            "artist_name": l.artist_name,
            "avatar": l.artist_avatar,
            "salon_id": l.salon_id,
            "salon_name": l.salon_name,
            "salon_avatar": l.salon_avatar,
            }
        listings.append(listing)
        artists_ids.append(l.artist_id)

    artists_ratings = Review.objects.filter(artist_id__in=artists_ids).values("artist_id").annotate(average_rating=Avg('rating'))

    final_map = {}
    for e in artists_ratings:
        final_map[e["artist_id"]] = e["average_rating"]

    for l in listings:
        rating = final_map.get(l['artist_id'], None)
        l["artist_rating"] = rating

    return render(request, 'service/service.html', {'listings': listings, "price_list": price_list})


def autocomplete_tags(request):
    result = Tags.objects.filter(tag__contains=request.GET["q"])
    if result:
        data = [r.tag for r in result]
    else:
        data = {}
    return HttpResponse(simplejson.dumps(data), content_type="application/json")


def search(request):
    styles = {
        "hairstyle": "hair",
        "nails-design": "nails",
        "make-up": "make up",
    }
    query = styles.get(request.GET.get("q", None), request.GET.get("q", None))
    lat = request.GET.get("lat", None)
    lng = request.GET.get("lng", None)
    budget = request.GET.get("budget", None)
    gender = request.GET.get("gender", None)
    rating = request.GET.get("rating", None)
    date = request.GET.get("date", None)
    hour = request.GET.get("hour", None)
    tags = request.GET.get("tags", None)
    sorted_by = request.GET.get("sorted_by", None)
    point = None
    start_price = 0
    end_price = 15000
    # point = Point(23.31326937672202, 42.68336526966131)
    type_of_order = ['listing_id', '-listing_id', '-likes', '-comments']
    currencies = dict(CURRENCY)
    if query:
        query = query.split(" ")
        if tags:
            tags = tags.split(',')
            query = query + tags
        sq = SQ()
        for q in query:
            sq.add(SQ(tags__contains=q), SQ.OR)
            sq.add(SQ(title__contains=q), SQ.OR)
            sq.add(SQ(description__contains=q), SQ.OR)
    else:
        sq = SQ()

    if budget:
        start_price = int(budget.split('-')[0])
        end_price = int(budget.split('-')[1])

    if gender:
        gender = int(gender)
        if gender == 0:
            gender = [0]
        elif gender == 2:
            gender = [2]
        else:
            gender = [0, 1, 2]
    else:
        gender = [0, 1, 2]

    if lat and lng and lat != 'undefined' and lng != 'undefined':
        print(lat, lng)
        lat = float(lat)
        lng = float(lng)
        point = Point(lat, lng)

    if date and date.isdigit():
        date = int(date)
    else:
        date = None

    if not (hour is None or hour == "-1"):
        hour = int(hour)
    else:
        hour = -1

    if rating:
        rating = int(rating)
    else:
        rating = 0

    if sorted_by:
        sorted_by = type_of_order[int(sorted_by)]
    else:
        sorted_by = 'listing_id'

    partial_query = SearchQuerySet().models(Listing).filter(sq)
    partial_query = [l.price for l in partial_query]

    if len(partial_query) >= 2:
        price_list = [min(partial_query), max(partial_query)]
    else:
        price_list = [0, 500]

    price_list = [min(price_list), max(price_list)]
    if point:
        _listings = SearchQuerySet().models(Listing).filter(sq).filter(
            gender__in=gender,
            price__gte=start_price,
            price__lte=end_price,
            status=1,
            rating__gte=rating).dwithin('location', point, D(km=1500000))
    else:
        _listings = SearchQuerySet().models(Listing).filter(sq).filter(
            gender__in=gender,
            price__gte=start_price,
            price__lte=end_price,
            status=1,
            rating__gte=rating)

    if date and not (hour is not None and hour == -1):
        ''' hour in seconds is the time in utc seconds from the date to the required time '''
        work_days = [("mon_start", "mon_end"), ("tues_start", "tues_end"), ("wed_start", "wed_end"), ("thurs_start", "thurs_end"), ("fri_start", "fri_end"), ("sat_start", "sat_end"), ("sun_start", "sun_end")]

        # get listings IDs which was already filtered and make in format (1,1,3,3,5)
        listings_ids = [l.listing_id for l in _listings]
        listings_ids = str(listings_ids)[1:-1] if listings_ids else 'NULL'

        # get the index of the day from the week
        week_days = datetime.datetime.fromtimestamp(date).strftime('%w')
        week_days = work_days[int(week_days)]

        # hour in seconds
        hour_in_seconds = 28800 + hour*1800

        # start range is a variable which will be used for the following things: time in seconds from booking start
        start_range = date + hour_in_seconds

        query = '''SELECT DISTINCT listing.id, listing.title, listing.likes, listing.price, listing.artist_id, listing.comments, listing.currency, listing.picture_cover, artist.lat, artist.lng, artist.style, artist.avatar, artist_user.first_name as artist_name, salon.id as salon_id, salon.avatar as salon_avatar, salon_user.first_name as salon_name
        FROM listings_listing AS listing
        JOIN artists_artist AS artist ON artist.id = listing.artist_id
        JOIN artists_worktime AS worktime ON worktime.artist_id = artist.id
        LEFT JOIN booking_booking AS booking ON booking.artist_id = artist.id
        LEFT JOIN artists_busy AS busy ON busy.artist_id = artist.id
        LEFT JOIN salons_salon AS salon ON artist.salon_id = salon.id
        LEFT JOIN auth_user AS salon_user ON salon.user_id = salon_user.id
        LEFT JOIN auth_user AS artist_user ON artist.user_id = artist_user.id
        WHERE listing.id IN ({listings_ids})
        AND worktime.{first_week_day} <= {hour} AND worktime.{second_week_day} >= ({hour} + listing.duration/1800)
        AND (booking.start_time >= listing.duration + {start_range}
        OR booking.end_time <= {start_range} OR booking.start_time IS NULL)
        AND (busy.start_time >= listing.duration + {start_range}
        OR busy.end_time <= {start_range} OR busy.start_time IS NULL)'''.format(listings_ids=listings_ids, first_week_day=week_days[0], hour=hour, second_week_day=week_days[1], start_range=start_range)

        cursor = connection.cursor()
        cursor.execute(query)
        _listings = dictfetchall(cursor)

        listings = []
        listing = {}
        for l in _listings:
            listing = {
                "lat": l["lat"],
                "lng": l["lng"],
                "id": l["id"],
                "picture": l["picture_cover"],
                "style": STYLE_INDEXES[l["style"]][1],
                "title": l["title"],
                "likes": l["likes"],
                "price": l["price"],
                "currency": currencies[l["currency"]],
                "comments": l["comments"],
                "artist_id": l["artist_id"],
                "artist_name": l["artist_name"],
                "avatar": MEDIA_ROOT + l["avatar"][7:] if l["avatar"] else '',
                "salon_id": l["salon_id"],
                "salon_name": l["salon_name"],
                "salon_avatar": MEDIA_ROOT + l["salon_avatar"][7:] if l["salon_avatar"] else ''
            }
            listings.append(listing)
    elif date:
        work_days = [("mon_start", "mon_end"), ("tues_start", "tues_end"), ("wed_start", "wed_end"), ("thurs_start", "thurs_end"), ("fri_start", "fri_end"), ("sat_start", "sat_end"), ("sun_start", "sun_end")]

        listings_ids = [l.listing_id for l in _listings]
        listings_ids = str(listings_ids)[1:-1] if listings_ids else 'NULL'

        week_days = datetime.datetime.fromtimestamp(date).strftime('%w')
        week_days = work_days[int(week_days)]

        query = '''SELECT DISTINCT listing.id, listing.title, listing.likes, listing.price, listing.artist_id, listing.comments, listing.currency, listing.picture_cover, artist.lat, artist.lng, artist.style, artist.avatar, artist_user.first_name as artist_name, salon.id as salon_id, salon.avatar as salon_avatar, salon_user.first_name as salon_name
            FROM listings_listing AS listing
            JOIN artists_artist AS artist ON artist.id = listing.artist_id
            JOIN artists_worktime AS worktime ON worktime.artist_id = artist.id
            LEFT JOIN booking_booking AS booking ON booking.artist_id = artist.id
            LEFT JOIN artists_busy AS busy ON busy.artist_id = artist.id
            LEFT JOIN salons_salon AS salon ON artist.salon_id = salon.id
            LEFT JOIN auth_user AS salon_user ON salon.user_id = salon_user.id
            LEFT JOIN auth_user AS artist_user ON artist.user_id = artist_user.id
            WHERE listing.id IN ({listings_ids})
            AND NOT worktime.{week_day} = -1'''.format(listings_ids=listings_ids, week_day=week_days[0])

        cursor = connection.cursor()
        cursor.execute(query)
        _listings = dictfetchall(cursor)

        listings = []
        listing = {}
        for l in _listings:
            listing = {
                "lat": l["lat"],
                "lng": l["lng"],
                "id": l["id"],
                "picture": l["picture_cover"],
                "style": STYLE_INDEXES[l["style"]][1],
                "title": l["title"],
                "likes": l["likes"],
                "price": l["price"],
                "currency": currencies[l["currency"]],
                "comments": l["comments"],
                "artist_id": l["artist_id"],
                "artist_name": l["artist_name"],
                "avatar": MEDIA_ROOT + l["avatar"][7:] if l["avatar"] else '',
                "salon_id": l["salon_id"],
                "salon_name": l["salon_name"],
                "salon_avatar": MEDIA_ROOT + l["salon_avatar"][7:] if l["salon_avatar"] else ''
            }
            listings.append(listing)

    else:
        listings = []
        listing = {}
        for l in _listings:
            listing = {
                "lat": l.location.x,
                "lng": l.location.y,
                "id": l.listing_id,
                "picture": l.get_picture,
                "style": l.style,
                "title": l.title,
                "likes": l.likes,
                "price": l.price,
                "currency": currencies[l.currency],
                "comments": l.comments,
                "artist_id": l.artist_id,
                "artist_name": l.artist_name,
                "avatar": l.artist_avatar,
                "salon_id": l.salon_id,
                "salon_name": l.salon_name,
                "salon_avatar": l.salon_avatar,
            }
            listings.append(listing)

    artists_ids = [l["artist_id"] for l in listings]
    artists_ratings = Review.objects.filter(artist_id__in=artists_ids).values("artist_id").annotate(average_rating=Avg('rating'))
    final_map = {}
    for e in artists_ratings:
        final_map[e["artist_id"]] = e["average_rating"]

    for l in listings:
        rating = final_map.get(l['artist_id'], None)
        l["artist_rating"] = rating

    return render(request, 'service/service.html', {"listings": listings, "price_list": price_list})


def get_hint(request):
    types = {"profiles": 0, "artists": 1, "salons": 2}
    next_id = request.GET.get("next_id", None)
    if next_id:
        hint = Hint.objects.get(id=next_id)
        data = {
            "title": hint.title,
            "img": '/media' + hint.media.path.split("/media")[1],
            "text": hint.description,
        }
    else:
        hints = Hint.objects.filter(group=types[request.user.related_with]).order_by("priority")
        data = {
            "title": hints[0].title,
            "img": '/media' + hints[0].media.path.split("/media")[1],
            "text": hints[0].description,
            "all": [h.id for h in hints],
        }

    return HttpResponse(simplejson.dumps(data), content_type="application/json")
