from django.db import connection
from django.http import HttpResponse
from django.utils import simplejson
from django.shortcuts import render

from glamazer.notifications.models import Notification
from glamazer.core.helpers import paginator, dictfetchall
from glamazer.settings import MEDIA_ROOT, STATIC_URL


def get_notifications(request):
    user = request.user
    receiver_id = user.id

    query = '''
    SELECT n.id, COALESCE(profile.avatar, artist.avatar, salon.avatar) AS avatar, n.short_text AS text, n.time AS time, n.is_readed AS is_readed, n.sender_id AS sender_id
    FROM notifications_notification as n
    INNER JOIN auth_user AS _user ON n.sender_id = _user.id
    LEFT JOIN users_profile AS profile ON _user.id = profile.user_id
    LEFT JOIN artists_artist AS artist ON _user.id = artist.user_id
    LEFT JOIN salons_salon AS salon ON _user.id = salon.user_id
    WHERE n.receiver_id = %s
    ORDER BY n.id DESC
    LIMIT 5;
    '''

    if user.related_with == 'salons':
        receiver_id = user.salon.id
        query = '''
        SELECT DISTINCT n.id, COALESCE(profile.avatar, artist.avatar, salon.avatar) AS avatar, n.short_text AS text, n.time AS time, n.is_readed AS is_readed, n.sender_id AS sender_id
        FROM salons_salon AS s
        INNER JOIN artists_artist AS a ON s.id = a.salon_id
        INNER JOIN auth_user AS u ON (a.user_id = u.id) or (u.id = '''+str(user.id)+''')
        INNER JOIN notifications_notification AS n ON n.receiver_id = u.id
        LEFT JOIN users_profile AS profile ON n.sender_id = profile.user_id
        LEFT JOIN artists_artist AS artist ON n.sender_id = artist.user_id
        LEFT JOIN salons_salon AS salon ON n.sender_id = salon.user_id
        WHERE s.id = %s
        ORDER BY n.id DESC
        LIMIT 5;
        '''

    cursor = connection.cursor()
    cursor.execute(query, [receiver_id])
    notifications = dictfetchall(cursor)
    _notifications = []
    for n in notifications:
        if n["sender_id"] == 1:
            n["avatar"] = "{0}img/logo_old.png".format(STATIC_URL)
        _notifications.append(n["id"])

    _notifications = Notification.objects.filter(id__in=_notifications).update(is_readed=True)

    return HttpResponse(simplejson.dumps(notifications), content_type="application/json")


def get_notification_count(request):
    user = request.user
    data = 0

    if user.related_with == "profiles":
        data = user.profile.get_notification_count()
    elif user.related_with == "artists":
        data = user.artist.get_notification_count()
    else:
        data = user.salon.get_notification_count()

    return HttpResponse(simplejson.dumps(data), content_type="application/json")


def show_notifications(request):
    user = request.user
    receiver_id = user.id
    query = '''
    SELECT n.id, COALESCE(profile.avatar, artist.avatar, salon.avatar) AS avatar, n.long_text AS text, n.time AS time, n.is_readed AS is_readed, n.sender_id AS sender_id
    FROM notifications_notification as n
    INNER JOIN auth_user AS _user ON n.sender_id = _user.id
    LEFT JOIN users_profile AS profile ON _user.id = profile.user_id
    LEFT JOIN artists_artist AS artist ON _user.id = artist.user_id
    LEFT JOIN salons_salon AS salon ON _user.id = salon.user_id
    WHERE n.receiver_id = %s
    ORDER BY n.id DESC
    '''

    if user.related_with == 'salons':
        receiver_id = user.salon.id
        query = '''
        SELECT DISTINCT (n.id), COALESCE(profile.avatar, artist.avatar, salon.avatar) AS avatar, n.long_text AS text, n.time AS time, n.is_readed AS is_readed, n.sender_id AS sender_id
        FROM salons_salon AS s
        INNER JOIN artists_artist AS a ON s.id = a.salon_id
        INNER JOIN auth_user AS u ON (a.user_id = u.id) OR (u.id = '''+str(user.id)+''')
        INNER JOIN notifications_notification AS n ON n.receiver_id = u.id
        LEFT JOIN users_profile AS profile ON n.sender_id = profile.user_id
        LEFT JOIN artists_artist AS artist ON n.sender_id = artist.user_id
        LEFT JOIN salons_salon AS salon ON n.sender_id = salon.user_id
        WHERE s.id = %s
        ORDER BY n.id DESC
        '''

    cursor = connection.cursor()
    cursor.execute(query, [receiver_id])
    notifications = dictfetchall(cursor)
    _notifications = []
    for n in notifications:
        n["avatar"] = MEDIA_ROOT + n["avatar"][7:] if n["avatar"] else ""
        _notifications.append(n["id"])

    _notifications = Notification.objects.filter(id__in=_notifications).update(is_readed=True)

    notifications = paginator(request, notifications, 10)

    return render(request, 'notifications/notifications.html', {'notifications': notifications})
