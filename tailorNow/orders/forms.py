from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['category', 'measurements', 'fabric_info', 'reference_photo', 'is_urgent']
        widgets = {
            'measurements': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter detailed measurements (e.g., chest: 40, waist: 32, sleeve: 24)'}),
            'fabric_info': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Describe fabric type, color, and quantity (e.g., 2 meters blue cotton)'})
        }

