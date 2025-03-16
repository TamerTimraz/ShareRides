from django.contrib import admin
from vehicleLending.models import User
from .models import *

# Register your models here.
admin.site.register(User)
admin.site.register(Vehicle)
admin.site.register(Collection)