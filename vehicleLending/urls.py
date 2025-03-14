from django.urls import path
from . import views

app_name = 'vehicleLending'  # Replace with your app name

urlpatterns = [
    path('', views.login_view, name='login'),  # the index page
    path('dashboard/patron', views.patron_dashboard, name='patron_dashboard'),
    path('dashboard/librarian', views.librarian_dashboard, name='librarian_dashboard'),
    path('sign-out', views.sign_out, name='sign_out'),
    path('auth-receiver', views.auth_receiver, name='auth_receiver'),
    path('profile', views.profile_view, name='profile'),
    path('vehicle/<int:vehicle_id>', views.item_desc, name='details'),
    path('add-vehicle', views.add_vehicle, name='add_vehicle')
]