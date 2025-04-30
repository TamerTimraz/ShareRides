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
    path('add-vehicle/<str:collection_name>', views.add_vehicle, name='add_vehicle_inside_collection'),
    path('edit_vehicle/<int:vehicle_id>', views.edit_vehicle, name='edit_vehicle'),
    path('delete_vehicle/<int:vehicle_id>', views.delete_vehicle, name='delete_vehicle'),
    path('add-collection', views.add_collection, name='add_collection'),
    path('edit_collection/<str:collection_name>', views.edit_collection, name='edit_collection'),
    path('remove-collection', views.remove_collection, name='remove_collection'),
    path('about', views.about, name='about'),
    path('search/', views.search_results, name='search'),
    path('collection_search/', views.collection_search_results, name='collection_search'),
    path('all',views.all_vehicles, name='all'),
    path('map', views.map_view, name='map'),
    path('vehicle/<int:vehicle_id>/request', views.request_borrow, name='request_borrow'),
    path('request/<int:request_id>/<str:response>', views.respond_to_request, name='respond_to_request'),
    path('requested', views.my_vehicles, name='my_vehicles'),
    path('requested/vehicle/<int:vehicle_id>/requests', views.vehicle_requests, name='vehicle_requests'),
    path('requested-vehicles', views.requested_vehicles, name='requested_vehicles'),
    path('return-vehicle/<int:vehicle_id>', views.return_vehicle, name='return_vehicle'),
    path('promote-patron/', views.promote_patron, name='promote_patron'),
    path('review/<int:review_id>/delete', views.delete_review, name='delete_review'),
    path('request-private-collection/', views.request_private_collection, name='request_private_collection'),
    # Access request management
    path('access-requests/', views.manage_access_requests, name='manage_access_requests'),
    path('access-request/<int:request_id>/<str:action>/', views.process_access_request, name='process_access_request'),
    path('remove-vehicle/', views.remove_vehicle, name='remove_vehicle'),
    path('add_vehicle_to_collection/<int:vehicle_id>/<int:collection_id>/', views.add_vehicle_to_collection, name='add_vehicle_to_collection'),
    path('remove_vehicle_from_collection/<int:vehicle_id>/<int:collection_id>/', views.remove_vehicle_from_collection, name='remove_vehicle_from_collection'),

# ###IGNORE###    
#    path('dev-login/', views.dev_login_as_librarian, name='dev_login'),

]