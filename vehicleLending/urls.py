from django.urls import path
from . import views

app_name = 'vehicleLending'  # Replace with your app name

urlpatterns = [
    path('', views.login_view, name='login'),  # the index page
    path('homepage', views.home_page, name='home_page'),
    path('sign-out', views.sign_out, name='sign_out'),
    path('auth-receiver', views.auth_receiver, name='auth_receiver'),
]