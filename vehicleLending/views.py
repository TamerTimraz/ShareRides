import os

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from google.oauth2 import id_token
from google.auth.transport import requests
from django.conf import settings
from django.urls import reverse
from .models import *
from django.contrib.auth import login, logout, get_user_model
from .forms import VehicleForm, ProfilePictureForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods

# Create your views here.

@csrf_exempt
def login_view(request):
    #if(request.user != None):
     #   return redirect('vehicleLending:home')
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

    user, created = User.objects.get_or_create(email=email, defaults={'name': name})

    login(request, user) # sets session info

    return redirect('vehicleLending:home')

def sign_out(request):
    logout(request)
    return redirect('vehicleLending:login')

def select_collection(request):
    public_collections = Collection.objects.filter(private_collection=False)
    
    if request.user.is_authenticated:
        if request.user.user_type == 'librarian':
            all_collections = Collection.objects.all()
            private_collections = Collection.objects.filter(private_collection=True)
        else:  # patron
            all_collections = Collection.objects.filter(creator=request.user)
            private_collections = Collection.objects.filter(users_with_access=request.user, private_collection=True)
    else:  # guest user
        all_collections = []
        private_collections = []
        
    return render(request, 'vehicleLending/select_collection.html', {
        'public_collections': public_collections, 
        'private_collections': private_collections,
        'all_collections': all_collections
    })

def select_vehicle(request, collection_name: str):
    collection = get_object_or_404(Collection, name=collection_name)
    vehicles = collection.vehicles.all()
    context = {"collection_name": collection_name, "vehicles": vehicles, "collection": collection}
    return render(request, 'vehicleLending/select_vehicle.html', context)

def item_desc(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    user = (request.user)
    return render(request,'vehicleLending/item_desc.html', {'vehicle': vehicle,'user':user})


def add_vehicle(request):
    # only librarians can access page
    if not request.user.is_authenticated or request.user.user_type != 'librarian':
        return redirect('vehicleLending:home')

    if request.method == 'POST':
        form = VehicleForm(request.POST, request.FILES)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.lender = request.user
            vehicle.save()
            return redirect(reverse('vehicleLending:details',args=[vehicle.id]))
        else:
            print(form.errors)
    else:
        form = VehicleForm()
    return render(request,'vehicleLending/add_vehicle.html',{'form':form})

def edit_vehicle(request, vehicle_id: int):
    if not request.user.is_authenticated or request.user.user_type != 'librarian':
        return redirect('vehicleLending:home')
    
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)

    if request.method == 'POST':
        form = VehicleForm(request.POST, request.FILES, instance=vehicle)
        if form.is_valid():
            form.save()
            return redirect(reverse('vehicleLending:details', args=[vehicle.id]))
    else:
        form = VehicleForm(instance=vehicle)
    return render(request, 'vehicleLending/add_vehicle.html', {'form': form, 'vehicle': vehicle})

def delete_vehicle(request, vehicle_id: int):
    if not request.user.is_authenticated or request.user.user_type != 'librarian':
        return redirect('vehicleLending:home')

    vehicle = get_object_or_404(Vehicle, id=vehicle_id)

    vehicle.delete()
    return redirect('vehicleLending:home')
    

def profile_view(request):
    if not request.user.is_authenticated:
        return redirect('vehicleLending:login')

    user = request.user
    if request.method == 'POST':
        form = ProfilePictureForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('vehicleLending:profile')
    else:
        form = ProfilePictureForm(instance=user)
    return render(request, 'vehicleLending/profile.html', {'form': form, 'user': user})

def delete_profile_picture(request):
    if not request.user.is_authenticated:
        return redirect('vehicleLending:login')
    
    user = request.user
    if user.profile_pic:
        user.profile_pic.delete(save=False)  # deletes from S3
        user.profile_pic = None
        user.save()
    return redirect('vehicleLending:profile')

def about(request):
    path = os.path.join(settings.BASE_DIR, 'vehicleLending', 'static', 'about', 'summary.txt')
    with open(path, 'r') as file:
        summary = file.read()
    quote = "ShareRides is transforming how we think about car sharing, bringing convenience and community together."
    policies = [
        "Insurance requirements",
        "Vehicle eligibility",
        "Vehicle maintenance",
        "Cleanliness",
        "Driver background checks",
        "Refueling",
    ]

    context = {'summary': summary, 'quote': quote, 'policies': policies}
    return render(request, 'vehicleLending/about.html', context)

def search_results(request):
    query = request.GET.get('query')

    vehicles = Vehicle.objects.filter(make__icontains=query)
    vehicles = [{"text": str(vehicle), "url": f"vehicle/{vehicle.id}"} for vehicle in vehicles]

    public_collections = Collection.objects.filter(name__icontains=query, private_collection=False)
    public_collections = [{"text": f"COLLECTION {str(collection)}", "url": f"collection/{collection.name}"} for collection in public_collections]

    if request.user.is_authenticated and request.user.user_type == 'librarian':
        private_collections = Collection.objects.filter(name__icontains=query, private_collection=True)
    elif request.user.is_authenticated and request.user.user_type == 'patron':
        private_collections = Collection.objects.filter(name__icontains=query, users_with_access=request.user, private_collection=True)
    else: # guest user
        private_collections = list()
    private_collections = [{"text": f"COLLECTION {str(collection)}", "url": f"collection/{collection.name}"} for collection in private_collections]

    results = vehicles + public_collections + private_collections
    if len(results) == 0:
        results = [{"text": "No results found", "url": "javascript:void(0)"}]
    elif len(results) > 8:
        results = results[:8]
    return JsonResponse({'results': results})


def all_vehicles(request):
    vehicles = Vehicle.objects.all()
    context = {"vehicles": vehicles}
    return render(request, 'vehicleLending/all_vehicles.html',context)


def add_collection(request):
    # Both librarians and patrons can create collections
    if not request.user.is_authenticated:
        return redirect('vehicleLending:home')
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        image = request.POST.get('image', '')
        
        # Only librarians can make collections private
        private_collection = False
        if request.user.user_type == 'librarian' and 'private_collection' in request.POST:
            private_collection = True
        
        # Create and save the collection
        collection = Collection(
            name=name,
            description=description,
            private_collection=private_collection,
            creator=request.user
        )
        
        if image:
            collection.image = image
            
        collection.save()
        
        return redirect('vehicleLending:home')
    
    return redirect('vehicleLending:home')

@login_required
def edit_collection(request, collection_name: str):
    collection = get_object_or_404(Collection, name=collection_name)

    if not request.user.is_authenticated:
        return redirect('vehicleLending:home')
    
    if request.method == 'POST':
        collection.name = request.POST.get('name')
        collection.description = request.POST.get('description')
        if request.POST.get('image', '') != '':
            collection.image = request.POST.get('image', '')
        collection.private_collection = request.user.user_type == 'librarian' and 'private_collection' in request.POST
        
        collection.save()
    
    return redirect('vehicleLending:home')

@login_required
def remove_collection(request):
    # Both librarians and patrons can remove collections they created
    if not request.user.is_authenticated:
        return redirect('vehicleLending:home')
    
    if request.method == 'POST':
        collection_id = request.POST.get('collection_id')
        
        try:
            collection = Collection.objects.get(id=collection_id)
            
            # Check if user is the creator of the collection
            if collection.creator == request.user:
                collection.delete()
            
        except Collection.DoesNotExist:
            pass
            
    return redirect('vehicleLending:home')

@login_required
def request_borrow(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    
    if vehicle.lender == request.user:
        messages.error(request, "You cannot request to borrow your own vehicle.")
        return redirect(reverse('vehicleLending:details', args=[vehicle_id]))
    
    borrow_request, created = BorrowRequest.objects.get_or_create(
        vehicle=vehicle,
        requester=request.user,
        lender=vehicle.lender,
        status='pending'
    )

    if created:
        messages.success(request, "Your borrow request has been submitted")
    else:
        messages.info(request, "You have already requested to borrow this vehicle")
    
    return redirect(reverse('vehicleLending:details', args=[vehicle_id]))

@login_required
def manage_requests(request):
    if request.user.user_type != 'librarian':
        messages.error(request, "You do not have permission to access this page.")
        return redirect('vehicleLending:home')
    
    requests = BorrowRequest.objects.filter(lender=request.user, status='pending')
    return render(request, 'vehicleLending/manage_requests.html', {'requests': requests})

@login_required
def respond_to_request(request, request_id, response):
    borrow_request = get_object_or_404(BorrowRequest, id=request_id, lender=request.user)
    if response == 'accept':
        borrow_request.status = 'accepted'
        borrow_request.vehicle.is_available = False
        borrow_request.vehicle.save()
    elif response == 'deny':
        borrow_request.status = 'denied'
    else:
        return redirect('vehicleLending:manage_requests')
    
    borrow_request.save()
    return redirect('vehicleLending:manage_requests')

@login_required
@require_http_methods(["GET", "POST"])
def promote_patron(request):

    # Temporary fix, may update later to only display to librarians so no need for check.
    if request.user.user_type != 'librarian':
        messages.error(request, "You do not have permission to access this page.")
        return redirect('vehicleLending:home')

    patrons = User.objects.filter(user_type='patron')

    if request.method == 'POST':
        #When selected
        selected_id = request.POST.get('patron_id')
        try:
            user_to_promote = User.objects.get(id=selected_id, user_type='patron')
            user_to_promote.user_type = 'librarian'
            user_to_promote.save()
            messages.success(request, f"{user_to_promote.name} was promoted to librarian.")
            return redirect('vehicleLending:promote_patron')
        except User.DoesNotExist:
            messages.error(request, "That user was not found or is already a librarian.")

    # Stay in page
    return render(request, 'vehicleLending/promote_patron.html', {'patrons': patrons})

####-----IGNORE----_#####
# def dev_login_as_librarian(request):
#     if not settings.DEBUG:
#         return HttpResponse("Not allowed in production.")

#     librarian = User.objects.filter(user_type='librarian').first()
#     if librarian:
#         login(request, librarian)
#         return redirect('vehicleLending:promote_patron')
#     return HttpResponse("No librarian user found.")
