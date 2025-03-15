from django import forms
from .models import User, Vehicle

class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profile_pic']

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields=["type",'make','model','year','details','is_available', 'image']
        exclude = ()
        widgets = {
            'details': forms.Textarea(attrs={'rows':4}),
            'type': forms.Select(choices=[
                ('car','Car'),
                ('bike','Bike'),
                ('truck','Truck'),
                ('van','Van'),
            ])
        }
