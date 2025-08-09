from django import forms
from .models import CustomUser

class CustomUserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = CustomUser
        fields = ('email', 'password')


class TailorRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = CustomUser
        fields = ('email', 'password')
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'tailor'
        user.is_approved = False
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

class AvailabilityForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['is_available']
        widgets = {
            'is_available': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

