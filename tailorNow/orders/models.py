from django.db import models
from django.conf import settings

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

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

    def __str__(self):
        return f"Order {self.id} - {self.category.name if self.category else 'N/A'}"
