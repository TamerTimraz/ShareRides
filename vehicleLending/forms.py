from django import forms
from .models import User, Vehicle

class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profile_pic']
        widgets = {
            'profile_pic': forms.FileInput()
        }

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields=["vehicle_type",'make','model','year','is_available','image','location','description']
        exclude = ()
        widgets = {
            'vehicle_type': forms.Select(choices=[
                ('car','Car'),
                ('bike','Bike'),
                ('truck','Truck'),
                ('van','Van'),
            ])
        }
