from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.auth.decorators import login_required
from tailorNow.orders.models import Order
from .models import Payment


@login_required
def create_checkout_session(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    if order.is_paid:
        return redirect('orders:order_detail', order_id=order.id)

    amount_cents = order.price_cents or 0
    if amount_cents <= 0:
        return HttpResponseBadRequest('Order has no payable amount')

    try:
        import stripe
    except ImportError:
        return HttpResponseBadRequest('Payments unavailable: Stripe SDK not installed')

    stripe.api_key = settings.STRIPE_SECRET_KEY

    domain_url = request.build_absolute_uri('/')
    success_url = domain_url + f"orders/orders/{order.id}?paid=1"
    cancel_url = domain_url + f"orders/orders/{order.id}?canceled=1"

    payment, _ = Payment.objects.get_or_create(
        order=order,
        defaults={
            'amount_cents': amount_cents,
            'currency': settings.STRIPE_CURRENCY,
        }
    )

    session = stripe.checkout.Session.create(
        mode='payment',
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': settings.STRIPE_CURRENCY,
                'unit_amount': amount_cents,
                'product_data': {
                    'name': f'TailorNow Order #{order.id}',
                },
            },
            'quantity': 1,
        }],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={'order_id': str(order.id)},
    )

    payment.provider_session_id = session['id']
    payment.provider_payment_intent = session.get('payment_intent', '')
    payment.status = 'created'
    payment.save(update_fields=['provider_session_id', 'provider_payment_intent', 'status'])

    return redirect(session.url)


@csrf_exempt
@require_POST
def stripe_webhook(request):
    try:
        import stripe
    except ImportError:
        return JsonResponse({'ok': False, 'error': 'stripe_not_installed'}, status=400)

    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    endpoint_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')
    event = None

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
    except Exception:
        return JsonResponse({'ok': False}, status=400)

    if event['type'] == 'checkout.session.completed':
        data = event['data']['object']
        order_id = data.get('metadata', {}).get('order_id')
        if order_id:
            try:
                order = Order.objects.get(id=order_id)
                Payment.objects.filter(order=order).update(status='succeeded')
                order.is_paid = True
                order.payment_reference = data.get('id', '')
                order.save(update_fields=['is_paid', 'payment_reference'])
            except Order.DoesNotExist:
                pass

    return JsonResponse({'ok': True})


