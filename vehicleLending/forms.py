from django import forms
from .models import User

class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profile_pic']