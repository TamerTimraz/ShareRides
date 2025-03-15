from vehicleLending.models import User, Vehicle
from django import forms

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields=["type",'make','model','year','details','is_available']
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