from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.postgres.fields import JSONField
from django.utils.timezone import now

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a user with an email instead of a username"""
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

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

    objects = CustomUserManager()

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
    vehicle_type = models.CharField(max_length=255, choices=VEHICLE_TYPES)
    lender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='vehicles'
    )
    make = models.CharField(max_length=255, default='Unknown Make')
    model = models.CharField(max_length=255, default='Unknown Model')
    year = models.CharField(max_length=255, default='Unknown Year')
    is_requested = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    location = models.CharField(max_length=255, default='Unknown')
    image = models.ImageField(upload_to=vehicle_directory_path, blank=True, null=True)
    description = models.CharField(max_length=255,null=True,blank=True)
    @property
    def title(self):
        return f"{self.year} {self.make} {self.model}"
    def delete(self, *args, **kwargs):
        # delete image from S3 when vehicle is deleted
        if self.image:
            self.image.delete(save=False)
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.vehicle_type.upper()} {self.make} {self.model} {self.year} {self.lender}"

class Collection(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    vehicles = models.ManyToManyField(Vehicle, related_name='collections', blank=True)
    image = models.URLField(blank=True, null=True, default="https://media.istockphoto.com/id/1055079680/vector/black-linear-photo-camera-like-no-image-available.jpg?s=612x612&w=0&k=20&c=P1DebpeMIAtXj_ZbVsKVvg-duuL0v9DlrOZUvPG6UJk=")
    users_with_access = models.ManyToManyField(User, related_name='private_collections', blank=True)
    private_collection = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({'private' if self.private_collection else 'public'})"
    
