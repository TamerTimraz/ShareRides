from django.urls import path
from . import views

app_name = 'vehicleLending'  # Replace with your app name

urlpatterns = [
    path('', views.login_view, name='login'),  # the index page
    path('sign_out', views.sign_out, name='sign_out'),
    path('auth-receiver', views.auth_receiver, name='auth_receiver'),
    path('profile', views.profile_view, name='profile'),
    path('profile/delete-profile-pic', views.delete_profile_picture, name="delete_profile_pic"),
    path('home', views.select_collection, name='home'),
    path('vehicle/<int:vehicle_id>', views.item_desc, name='details'),
    path('collection/<str:collection_name>', views.select_vehicle, name='collection'),
    path('add-vehicle', views.add_vehicle, name='add_vehicle'),
    path('add-collection', views.add_collection, name='add_collection'),
    path('remove-collection', views.remove_collection, name='remove_collection'),
    path('about', views.about, name='about'),
    path('search/', views.search_results, name='search'),
    path('all',views.all_vehicles, name='all'),
    path('vehicle/<int:vehicle_id>/request', views.request_borrow, name='request_borrow'),
    path('request/<int:request_id>/<str:response>', views.respond_to_request, name='respond_to_request'),
    path('my-vehicles', views.my_vehicles, name='my_vehicles'),
    path('my-vehicles/vehicle/<int:vehicle_id>/requests', views.vehicle_requests, name='vehicle_requests')
]