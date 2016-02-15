from time import strftime

from django.db import models
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

from glamazer.booking.models import Booking
from glamazer.settings import PAYMENTS_METHOD, WITHDRAW_STATUS


class Payment(models.Model):
    booking = models.ForeignKey(Booking)
    payment_method = models.IntegerField(choices=tuple(enumerate(PAYMENTS_METHOD)))
    state = models.CharField(max_length=128)
    create_time = models.IntegerField()
    valid_until = models.IntegerField(max_length=128, blank=True, null=True)
    price = models.FloatField()
    currency = models.CharField(max_length=128)
    payer_id = models.CharField(max_length=128, blank=True, null=True)
    payment_id = models.CharField(max_length=128, blank=True, null=True)
    authorization_id = models.CharField(max_length=128)
    transaction_id = models.CharField(max_length=128, null=True)
    current_status = models.CharField(max_length=128, default="authorized")
    last_updated = models.DateTimeField(auto_now=True, auto_now_add=True)

    def get_method(self):
        return PAYMENTS_METHOD[self.method]


class Fee(models.Model):
    fee = models.IntegerField()
    comment = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    deactivated = models.DateTimeField(editable=True, null=True, blank=True)

    def save(self, force_insert=False, force_update=False, **kwargs):
        if not self.id:
            now = strftime("%Y-%m-%d %H:%M:%S")
            Fee.objects.filter(deactivated__isnull=True).update(deactivated=now)
        super(Fee, self).save(force_insert, force_update)


class ReceiverAccount(models.Model):
    user = models.ForeignKey(User)
    method = models.IntegerField(default=1)
    paypal_email = models.CharField(max_length=128, blank=True, null=True)
    bank_name = models.CharField(max_length=128, blank=True, null=True)
    branch = models.CharField(max_length=128, blank=True, null=True)
    payee = models.CharField(max_length=128, blank=True, null=True)
    iban = models.CharField(max_length=128, blank=True, null=True)
    swift = models.CharField(max_length=128, blank=True, null=True)

    def get_method(self):
        return PAYMENTS_METHOD[self.method]

    def user_link(self):
        url = '<a href="%s">%s</a>' % (reverse(("admin:auth_user_change"), args=(self.user.id, )), self.user.first_name)
        return url

    user_link.allow_tags = True
    user_link.short_description = "User"


class Withdraw(models.Model):
    user = models.ForeignKey(User)
    option = models.ForeignKey(ReceiverAccount)
    created = models.DateTimeField(auto_now_add=True)
    money = models.FloatField()
    method = models.IntegerField()
    status = models.IntegerField(default=0, choices=WITHDRAW_STATUS)

    def get_method(self):
        return PAYMENTS_METHOD[self.method]

    def get_status(self):
        return WITHDRAW_STATUS[self.status][1]

    def user_link(self):
        url = '<a href="%s">%s</a>' % (reverse(("admin:auth_user_change"), args=(self.user.id, )), self.user.first_name)
        return url

    def receiver_acc_link(self):
        url = '<a href="%s">%s</a>' % (reverse(("admin:payments_receiveraccount_change"), args=(self.option.id, )), self.option_id)
        return url

    user_link.allow_tags = True
    user_link.short_description = "User"
    receiver_acc_link.allow_tags = True
    receiver_acc_link.short_description = "Bank Account"
