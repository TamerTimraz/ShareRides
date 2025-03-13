from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now

# Create your models here.

def user_directory_path(instance, filename):
    return f'profile_pictures/{instance.name}/{filename}'

class User(AbstractUser):
    username = None
    password = models.CharField(max_length=255, default="defaultpassword")
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    user_type = models.CharField(max_length=10, default='patron')
    date_joined = models.DateTimeField(default=now)
    profile_pic = models.ImageField(upload_to=user_directory_path, blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.email