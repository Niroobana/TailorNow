from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('checkout/<int:order_id>/', views.create_checkout_session, name='checkout'),
    path('stripe/webhook/', views.stripe_webhook, name='stripe_webhook'),
]



