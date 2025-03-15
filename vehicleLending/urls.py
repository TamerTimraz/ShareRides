from django.urls import path
from . import views

app_name = 'vehicleLending'  # Replace with your app name

urlpatterns = [
    path('', views.login_view, name='login'),  # the index page
    path('dashboard/patron', views.patron_dashboard, name='patron_dashboard'),
    path('dashboard/librarian', views.librarian_dashboard, name='librarian_dashboard'),
    path('sign_out', views.sign_out, name='sign_out'),
    path('auth-receiver', views.auth_receiver, name='auth_receiver'),
    path('home', views.select_collection, name='home'),
]