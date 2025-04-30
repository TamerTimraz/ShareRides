from django import forms
from .models import User, Vehicle, Collection, Review, VehicleImage
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory

class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profile_pic']
        exclude = ()

# class VehicleForm(forms.ModelForm):
#     class Meta:
#         model = Vehicle
#         fields=["vehicle_type",'make','model','year','is_available','image','location','description']
#         exclude = ()
#         widgets = {
#             'vehicle_type': forms.Select(choices=[
#                 ('car','Car'),
#                 ('bike','Bike'),
#                 ('truck','Truck'),
#                 ('van','Van'),
#             ]),
#             'location': forms.TextInput(attrs={
#                 'placeholder': 'Enter an address',
#                 'class': 'form-control',
#                 'autocomplete': 'off',  # Prevent browser autocomplete from interfering
#             }),
#             'description': forms.Textarea(attrs={
#                 'rows': 3,
#                 'class': 'form-control'
#             })
#         }

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = [
            "vehicle_type",
            "make",
            "model",
            "year",
            "location",
            "description",
        ]
        widgets = {
            "vehicle_type": forms.Select(attrs={
                "class": "form-select",
            }),
            "make": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. Toyota",
            }),
            "model": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. Camry",
            }),
            "year": forms.NumberInput(attrs={
                "class": "form-control",
                "placeholder": "e.g. 2023",
            }),
            "location": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Enter an address",
                "autocomplete": "off",  # Prevent browser autocomplete from interfering
            }),
            "description": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 4,
            }),
        }

class VehicleImageForm(forms.ModelForm):
    class Meta:
        model = VehicleImage
        fields = ['image']

VehicleImageFormSet = inlineformset_factory(
    Vehicle,
    VehicleImage,
    form=VehicleImageForm,
    extra=3,  # You can allow 3 images by default; change as needed
    can_delete=True
)

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
            'rating': forms.Select(attrs={'class': 'form-select mb-3'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }