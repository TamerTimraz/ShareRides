from django.shortcuts import render

import os

from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from google.oauth2 import id_token
from google.auth.transport import requests
from django.conf import settings
from .models import User, Vehicle
from django.contrib.auth import login, logout, get_user_model
from .forms import VehicleForm, ProfilePictureForm
from django.contrib.auth.decorators import login_required

# Create your views here.

@csrf_exempt
def login_view(request):
    return render(request, 'vehicleLending/login.html', {"google_client_id": settings.GOOGLE_OAUTH_CLIENT_ID})  

@csrf_exempt
def auth_receiver(request):
    """
    Google calls this URL after the user has signed in with their Google account.
    """
    token = request.POST['credential']

    try:
        user_data = id_token.verify_oauth2_token(
            token, requests.Request(), os.environ['GOOGLE_OAUTH_CLIENT_ID']
        )
    except ValueError:
        return HttpResponse(status=403)
    
    email = user_data.get('email')
    name = user_data.get('given_name')

    # checks if user exists, otherwise creates user
    #user, created = User.objects.get_or_create(email=email, defaults={'name': name})

    user, created = User.objects.get_or_create(email=email, defaults={'name': name})

    login(request, user) # sets session info

    if user.user_type == 'librarian':
        return redirect('vehicleLending:librarian_dashboard')
    else:
        return redirect('vehicleLending:patron_dashboard')

def home_page(request):
    return render(request, 'vehicleLending/homepage.html')

def patron_dashboard(request):
    user = request.user
    return render(request, 'vehicleLending/patron_dashboard.html', {'user': user})

def librarian_dashboard(request):
    user = request.user
    return render(request, 'vehicleLending/librarian_dashboard.html', {'user': user})

def sign_out(request):
    logout(request)
    return redirect('vehicleLending:login')

def item_desc(request,vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    user = (request.user)
    return render(request,'vehicleLending/item_desc.html', {'vehicle': vehicle})

@login_required
def add_vehicle(request):
    # add code to check if user is a librarian (only librarians can add vehicles)
    if request.method == 'POST':
        form = VehicleForm(request.POST, request.FILES)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.lender = request.user
            vehicle.save()
            return redirect('vehicleLending:librarian_dashboard')
        else:
            print(form.errors)
    else:
        form = VehicleForm()
    return render(request,'vehicleLending/add_vehicle.html',{'form':form})

@login_required
def profile_view(request):
    user = request.user
    if request.method == 'POST':
        form = ProfilePictureForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('vehicleLending:profile')
    else:
        form = ProfilePictureForm(instance=user)
    return render(request, 'vehicleLending/profile.html', {'form': form, 'user': user})