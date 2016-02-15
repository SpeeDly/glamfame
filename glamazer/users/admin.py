from django.contrib import admin
from django.contrib.admin import SimpleListFilter
from django.contrib.auth.models import User

from glamazer.users.models import Profile
from glamazer.artists.models import Artist, CancellationPolicy, ArtistPolicy
from glamazer.salons.models import Salon
from glamazer.listings.models import Listing
from glamazer.booking.models import Booking, ReportedProblems
from glamazer.payments.models import Payment, Fee, ReceiverAccount, Withdraw
from glamazer.reviews.models import WaitingForFeedback, Review
from glamazer.notifications.models import Notification, Hint
from glamazer.settings import STYLE_INDEXES


class StyleFilter(SimpleListFilter):
    title = 'Style'

    parameter_name = 'style'

    def lookups(self, request, model_admin):
        return STYLE_INDEXES

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(style=self.value())


class StepFilter(SimpleListFilter):
    title = 'Step'

    parameter_name = 'step'

    def lookups(self, request, model_admin):
        return ((2, "Step 2"), (3, "Step 3"), (4, "Step 4"), (0, "Finished"))

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(step=self.value())


class StatusFilter(SimpleListFilter):
    title = 'Status'

    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return ((0, "Pending"), (1, "Approved"), (2, "Rejected"))

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(status=self.value())


class ProfileAdmin(admin.ModelAdmin):
    readonly_fields = ('get_avatar_tag',)
    list_display = ('get_name', 'is_activated')
    exclude = ('avatar',)
    search_fields = ['user__first_name']
    list_filter = ('is_activated',)


class SalonAdmin(admin.ModelAdmin):
    readonly_fields = ('get_avatar_tag',)
    list_display = ('get_name', 'description', 'mobile_number', 'money', 'rating', 'get_step', 'is_activated')
    exclude = ('avatar',)
    search_fields = ['user__first_name']
    list_filter = (StepFilter, 'is_activated',)


class ArtistAdmin(admin.ModelAdmin):
    readonly_fields = ('get_avatar_tag',)
    list_display = ('get_name', 'salon_link', 'description', 'mobile_number', 'money', 'get_style_display', 'rating', 'get_step', 'is_activated')
    exclude = ('avatar',)
    search_fields = ['user__first_name']
    list_filter = (StepFilter, StyleFilter, 'is_activated')


class ListingAdmin(admin.ModelAdmin):
    readonly_fields = ('view_all_pictures',)
    list_display = ('title', 'artist', 'description', 'price', 'likes', 'duration', 'status', 'uploaded')
    search_fields = ['title', 'description']
    list_filter = (StyleFilter, 'price', 'duration', 'status', 'uploaded')
    list_editable = ('status',)
    exclude = ('metadata', 'picture_cover')


class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender_link', 'receiver_link', 'short_text', 'long_text', 'time', 'is_readed')


class BookingAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'artist_link', 'client_link', 'listing_link', 'comment', 'status', 'revenue')
    # search_fields = ['title', 'description']
    list_filter = (StatusFilter,)
    # exclude = ('metadata', 'picture_cover')


class CancellationPolicyAdmin(admin.ModelAdmin):
    list_display = ('cancellation_type', 'days_before', 'percent')
    search_fields = ['cancellation_policy']
    list_editable = ('days_before', 'percent', )
    list_filter = ('days_before', 'percent', )


class ArtistPolicyAdmin(admin.ModelAdmin):
    list_display = ('id', 'artist_link', 'cancellation_policy_link', 'status')
    list_editable = ('status', )
    list_filter = ('status',)


class FeeAdmin(admin.ModelAdmin):
    list_display = ('fee', 'created', 'comment', 'deactivated')
    list_filter = ('created', 'deactivated')
    exclude = ('fee', 'created', 'comment', 'deactivated',)


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'client_link', 'artist_link', 'listing_link', 'booking_link', "rating", "text", "created")
    list_filter = ('created',)


class WaitingForFeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'client_link', 'artist_link', 'listing_link', 'booking_link', 'token')


class ReceiverAccountAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_link', 'get_method', 'paypal_email', 'bank_name', 'branch', 'payee', 'iban', 'swift')


class WithdrawAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_link', 'receiver_acc_link', 'money', 'get_method', 'status', 'created')
    list_editable = ('status', )


class PaymentAdmin(admin.ModelAdmin):
    list_display = ("booking", "payment_method", "create_time", "valid_until", "price", "transaction_id", "authorization_id", "current_status", "last_updated")


class ReportedProblemsAdmin(admin.ModelAdmin):
    list_display = ("booking", "artist", "client", "listing", "comment", "status", "sender", "created")
    list_editable = ('status', )


class HintAdmin(admin.ModelAdmin):
    list_display = ("id", "group", "title", "media", "description", "priority",)
    list_editable = ("priority",)


def user_str(self):
    return self.first_name

User.__str__ = user_str

admin.site.unregister(User)
admin.site.register(User)

admin.site.register(Profile, ProfileAdmin)
admin.site.register(Artist, ArtistAdmin)
admin.site.register(Salon, SalonAdmin)
admin.site.register(Listing, ListingAdmin)
admin.site.register(Booking, BookingAdmin)
admin.site.register(Fee, FeeAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(CancellationPolicy, CancellationPolicyAdmin)
admin.site.register(ArtistPolicy, ArtistPolicyAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(WaitingForFeedback, WaitingForFeedbackAdmin)
admin.site.register(ReceiverAccount, ReceiverAccountAdmin)
admin.site.register(Withdraw, WithdrawAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(ReportedProblems, ReportedProblemsAdmin)
admin.site.register(Hint, HintAdmin)
