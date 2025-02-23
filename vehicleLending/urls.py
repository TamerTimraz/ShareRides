from django.urls import path
from . import views

app_name = 'your_app_name'  # Replace with your app name

urlpatterns = [
    path('', views.login_view, name='login'),  # the index page
    path('', views.sign_in, name='sign_in'),
    path('sign-out', views.sign_out, name='sign_out'),
    path('auth-receiver', views.auth_receiver, name='auth_receiver'),
]