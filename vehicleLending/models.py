from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import JSONField
from django.utils.timezone import now


def user_directory_path(instance, filename):
    return f'profile_pictures/{instance.email}/{filename}'

def vehicle_directory_path(instance, filename):
    return f'vehicles/{instance.lender.email}/{filename}'

class User(AbstractUser):
    USER_TYPES = [('patron','Patron'), ('librarian','Librarian')]

    username = None
    password = models.CharField(max_length=255, default="defaultpassword")
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='patron')
    date_joined = models.DateTimeField(default=now)
    profile_pic = models.ImageField(upload_to=user_directory_path, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def save(self, *args, **kwargs):
        # check if updating existing user with new profile pic
        if self.pk:
            existing_user = User.objects.filter(pk=self.pk).first()
            if existing_user and existing_user.profile_pic and self.profile_pic != existing_user.profile_pic:
                existing_user.profile_pic.delete(save=False) # delete old profile pic from S3

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # delete profile pic from S3 when user is deleted
        if self.profile_pic:
            self.profile_pic.delete(save=False)
        super().delete(*args, **kwargs)


    def __str__(self):
        return f"{self.name} ({self.email}), {self.user_type.upper()}"
    
class Vehicle(models.Model):
    VEHICLE_TYPES = [
        ('bicycle','Bicycle'),
        ('car','Car'),
        ('truck','Truck'),
        ('van','Van'),
        ('motorcycle','Motorcycle')
    ]
    type = models.CharField(max_length=255, choices=VEHICLE_TYPES)
    lender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='vehicles'
    )
    make = models.CharField(max_length=255, default='unknown')
    model = models.CharField(max_length=255, default='unknown')
    year = models.CharField(max_length=255, default='unknown')
    details = models.JSONField(blank=True,null=True)
    is_available = models.BooleanField(default=True)
    image = models.ImageField(upload_to=vehicle_directory_path, blank=True, null=True)

    def __str__(self):
        return f"{self.type.upper()} {self.make} {self.model} {self.year} {self.lender}"

class Collection(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    vehicles = models.ManyToManyField(Vehicle, related_name='collections', blank=True)
    image = models.URLField(blank=True, null=True, default="https://media.istockphoto.com/id/1055079680/vector/black-linear-photo-camera-like-no-image-available.jpg?s=612x612&w=0&k=20&c=P1DebpeMIAtXj_ZbVsKVvg-duuL0v9DlrOZUvPG6UJk=")
    users_with_access = models.ManyToManyField(User, related_name='private_collections', blank=True)
    private_collection = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({'private' if self.private_collection else 'public'})"
    
