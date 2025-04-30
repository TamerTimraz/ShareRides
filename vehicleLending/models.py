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
    return f'vehicles/{instance.vehicle.lender.email}/{filename}'

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
        ('Bicycle','Bicycle'),
        ('Car','Car'),
        ('Truck','Truck'),
        ('Van','Van'),
        ('Motorcycle','Motorcycle')
    ]

    vehicle_type = models.CharField(max_length=255, choices=VEHICLE_TYPES)
    lender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='vehicles'
    )

    make = models.CharField(max_length=255)
    model = models.CharField(max_length=255)
    year = models.CharField(max_length=255)
    is_available = models.BooleanField(default=True,blank=True,null=True)
    is_requested = models.BooleanField(default=True,blank=True,null=True)
    location = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    description = models.CharField(max_length=255,null=True,blank=True)

    private_collection = models.ForeignKey("Collection", related_name="collection", blank=True, null=True, on_delete=models.SET_NULL)

    @property
    def title(self):
        return f"{self.year} {self.make} {self.model}"
    
    def is_requested(self):
        return self.borrow_requests.filter(status='pending').exists()
    
    def delete(self, *args, **kwargs):
        # delete image from S3 when vehicle is deleted
        if self.image:
            self.image.delete(save=False)
        super().delete(*args, **kwargs)

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if not reviews:
            return None
        return round(sum([r.rating for r in reviews]) / len(reviews), 1)


    def __str__(self):
        return f"{self.vehicle_type.upper()} {self.make} {self.model} {self.year} {self.lender}"

class VehicleImage(models.Model):
    vehicle = models.ForeignKey('Vehicle', related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to=vehicle_directory_path)

    def __str__(self):
        return f"Image for {self.vehicle}"

class Collection(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    vehicles = models.ManyToManyField(Vehicle, related_name='collections', blank=True)
    image = models.URLField(blank=True, null=True, default="https://media.istockphoto.com/id/1055079680/vector/black-linear-photo-camera-like-no-image-available.jpg?s=612x612&w=0&k=20&c=P1DebpeMIAtXj_ZbVsKVvg-duuL0v9DlrOZUvPG6UJk=")
    users_with_access = models.ManyToManyField(User, related_name='private_collections', blank=True)
    private_collection = models.BooleanField(default=False)
    creator = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='created_collections', null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({'private' if self.private_collection else 'public'})"
    
class BorrowRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('denied', 'Denied')
    ]

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='borrow_requests')
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='borrow_requests')
    lender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lender_requests')
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default='pending')
    request_date = models.DateTimeField(default=now)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['vehicle', 'requester'], name='unique_vehicle_requester')
        ]

    def __str__(self):
        return f"Request by {self.requester} for {self.vehicle} - {self.status}"

class Review(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1 to 5 stars
    comment = models.TextField(blank=True)
    date = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.reviewer.name} - {self.rating} stars"

class CollectionAccessRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('denied', 'Denied'),
    ]
    
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name='access_requests')
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='collection_requests')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    request_date = models.DateTimeField(default=now)
    
    class Meta:
        unique_together = ('collection', 'requester')
    
    def __str__(self):
        return f"{self.requester.email} → {self.collection.name} ({self.status})"
