from django import forms
from .models import Order, Dispute, Feedback

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['category', 'measurements', 'fabric_info', 'reference_photo', 'is_urgent']
        widgets = {
            'measurements': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter detailed measurements (e.g., chest: 40, waist: 32, sleeve: 24)'}),
            'fabric_info': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Describe fabric type, color, and quantity (e.g., 2 meters blue cotton)'})
        }

class DisputeForm(forms.ModelForm):
    class Meta:
        model = Dispute
        fields = ['reason', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Provide a detailed description of the issue.'})
        }

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5, 'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Share your experience with this order (optional).', 'class': 'form-control'}),
        }
        labels = {
            'rating': 'Rating (1-5)'
        }


