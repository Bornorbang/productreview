from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UserProfile, Review



class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        # Add Bootstrap classes to form fields
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Username'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["product_name", "brand", "category", "seller", "title", "picture", "review", "rating"]

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["phone", "state", "profile_picture"]

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        self.fields['phone'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your phone number'
        })
        self.fields['state'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your state'
        })
        self.fields['profile_picture'].widget.attrs.update({
            'class': 'form-control-file'  # Bootstrap class for file input
        })