from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(
        max_length=100,
        blank=True,
        help_text="Bootstrap Icons class, e.g. 'bi-scissors' or 'bi-suit'")
    base_price_cents = models.PositiveIntegerField(default=0, help_text="Default base price (in cents)")
    urgent_surcharge_percent = models.PositiveIntegerField(default=0, help_text="Urgent surcharge percentage")

    def __str__(self):
        return self.name

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('assigned', 'Assigned'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='customer_orders')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    measurements = models.TextField(blank=True, help_text="Detailed measurements")
    fabric_info = models.TextField(blank=True, help_text="Type, color, quantity of fabric")
    reference_photo = models.ImageField(upload_to='order_photos/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_urgent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    assigned_tailor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_orders', limit_choices_to={'role': 'tailor', 'is_approved': True})
    # Payments
    price_cents = models.PositiveIntegerField(default=0, help_text="Amount to collect in cents")
    is_paid = models.BooleanField(default=False)
    payment_reference = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"Order {self.id} - {self.category.name if self.category else 'N/A'}"

    def compute_price_cents(self) -> int:
        if not self.category:
            return 0
        price = int(self.category.base_price_cents or 0)
        if self.is_urgent:
            percent = int(self.category.urgent_surcharge_percent or 0)
            price = price + round(price * (percent / 100.0))
        return int(price)

class Dispute(models.Model):
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('in_review', 'In Review'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    )

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='dispute')
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='raised_disputes')
    reason = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_disputes', limit_choices_to={'role': 'admin'})

    def __str__(self):
        return f"Dispute for Order {self.order.id} - {self.reason}"

class Feedback(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='feedback')
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='order_feedbacks')
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback for Order {self.order.id} - {self.rating}/5"
