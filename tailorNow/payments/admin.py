from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'amount_cents', 'currency', 'status', 'created_at')
    list_filter = ('status', 'currency')
    search_fields = ('order__id__iexact', 'provider_session_id', 'provider_payment_intent')



