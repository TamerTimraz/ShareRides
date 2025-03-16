from django.shortcuts import render

import os

from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from google.oauth2 import id_token
from google.auth.transport import requests
from django.conf import settings
from .models import *
from django.contrib.auth import login, logout, get_user_model
from .forms import VehicleForm
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

    return redirect('vehicleLending:home')

def home_page(request):
    return render(request, 'vehicleLending/homepage.html')

def sign_out(request):
    logout(request)
    return redirect('vehicleLending:login')

def select_collection(request):
    public_collections = Collection.objects.filter(private_collection=False)

    if request.user.is_authenticated and request.user.user_type == 'librarian':
        private_collections = Collection.objects.filter(private_collection=True)
    elif request.user.is_authenticated and request.user.user_type == 'patron':
        private_collections = Collection.objects.filter(users_with_access=request.user, private_collection=True)
    else: # guest user
        private_collections = []
    return render(request, 'vehicleLending/select_collection.html', {'public_collections': public_collections, 'private_collections': private_collections})

def select_vehicle(request, collection_name: str):
    collection = get_object_or_404(Collection, name=collection_name)
    vehicles = collection.vehicles.all()
    context = {"collection_name": collection_name, "vehicles": vehicles}
    return render(request, 'vehicleLending/select_vehicle.html', context)

def item_desc(request,vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    user = (request.user)
    return render(request,'vehicleLending/item_desc.html', {'vehicle': vehicle})

#@login_required
def add_vehicle(request):
    if request.method == 'POST':
        form = VehicleForm(request.POST)
        if form.is_valid():
            vehicle = form.save(commit=False)
            if request.user.is_authenticated:
                vehicle.lender = request.user

            #this is just for working without needing to sign in.
            else:
                vehicle.lender, created = User.objects.get_or_create(
                    email='default2@example.com',
                    defaults={'name': 'Default user'}
                )
            vehicle.save()
            return redirect('vehicleLending/librarian_dashboard.html')
        else:
            print(form.errors)
    else:
        form = VehicleForm()
    return render(request,'vehicleLending/add_vehicle.html',{'form':form})