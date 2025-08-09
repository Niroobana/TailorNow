from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from tailorNow.accounts.models import Notification

@receiver(post_save, sender=Notification)
def send_notification_email(sender, instance: Notification, created: bool, **kwargs):
    if not created:
        return
    # Respect feature flag
    if not getattr(settings, 'SEND_NOTIFICATION_EMAILS', False):
        return
    recipient_email = getattr(instance.recipient, 'email', None)
    if not recipient_email:
        return
    subject = "TailorNow Notification"
    message = instance.message
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@tailornow.local')
    try:
        send_mail(subject, message, from_email, [recipient_email], fail_silently=True)
    except Exception:
        # In dev we ignore email errors
        pass
