from django.db import models
from django.conf import settings


class Payment(models.Model):
    order = models.OneToOneField('orders.Order', on_delete=models.CASCADE, related_name='payment')
    amount_cents = models.PositiveIntegerField()
    currency = models.CharField(max_length=10, default='usd')
    provider = models.CharField(max_length=20, default='stripe')
    provider_session_id = models.CharField(max_length=255, blank=True)
    provider_payment_intent = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=30, default='created')  # created, succeeded, failed, canceled
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Payment for Order {self.order_id} - {self.status}"


