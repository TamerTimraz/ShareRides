from django.urls import path
from . import views

app_name = 'your_app_name'  # Replace with your app name

urlpatterns = [
    path('', views.login_view, name='login'),  # the index page
]