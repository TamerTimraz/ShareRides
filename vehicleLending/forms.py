from django import forms
from .models import User, Vehicle, Collection, Review

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

class CollectionForm(forms.ModelForm):
    class Meta:
        model = Collection
        fields = ['name', 'description', 'image', 'private_collection']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'image': forms.URLInput(attrs={'class': 'form-control'}),
            'private_collection': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(choices=[(i, f"{i} Star{'s' if i > 1 else ''}") for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Write your experience...'}),
        }