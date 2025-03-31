from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(User)
admin.site.register(Vehicle)
admin.site.register(BorrowRequest)

class CollectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'private_collection', 'get_allowed_users')
    
    def get_allowed_users(self, obj):
        return ", ".join([f"{user.name} ({user.email})" for user in obj.users_with_access.all()])
    
    get_allowed_users.short_description = "Allowed Users"

admin.site.register(Collection, CollectionAdmin)
