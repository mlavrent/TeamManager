from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SignUpForm(UserCreationForm):
    error_css_class = "error"
    required_css_class = "required"

    email = forms.EmailField(max_length=254, label="Email:")
    first_name = forms.CharField(max_length=30, label="First name:")
    last_name = forms.CharField(max_length=150, label="Last name:")

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
