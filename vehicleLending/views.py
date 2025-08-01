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
from .forms import VehicleForm, ProfilePictureForm, ReviewForm, VehicleImageFormSet
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db.models import Q

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
    name = f"{user_data.get('given_name')} {user_data.get('family_name')}"

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
            private_collections_with_access = Collection.objects.filter(private_collection=True)
        else:  # patron
            all_collections = Collection.objects.filter(creator=request.user)
            private_collections = Collection.objects.filter(private_collection=True)
            private_collections_with_access = Collection.objects.filter(users_with_access=request.user, private_collection=True)
    else:  # guest user
        all_collections = []
        private_collections = []
        private_collections_with_access = []
        
    return render(request, 'vehicleLending/select_collection.html', {
        'public_collections': public_collections, 
        'private_collections': private_collections,
        'all_collections': all_collections
    })

def select_vehicle(request, collection_name: str):
    collection = get_object_or_404(Collection, name=collection_name)
    vehicles = collection.vehicles.all()
    all_vehicles = [vehicle for vehicle in Vehicle.objects.all() if not vehicle.private_collection]
    is_patron_owner = request.user.is_authenticated and request.user.user_type == 'patron' and collection.creator == request.user
    creator = f"{collection.creator.name} ({collection.creator.email})" if collection.creator else "Unknown"
    authorized_patrons = [f"{user.name} ({user.email})" for user in collection.users_with_access.all()]
    context = {"collection_name": collection_name, "vehicles": vehicles, "collection": collection, "all_vehicles": all_vehicles, "is_patron_owner": is_patron_owner, "creator": creator, "authorized_patrons": authorized_patrons}
    return render(request, 'vehicleLending/select_vehicle.html', context)

def add_vehicle(request, collection_name=None):
    collection = None
    if collection_name:
        collection = get_object_or_404(Collection, name=collection_name)
    # only librarians can access page
    if not request.user.is_authenticated or request.user.user_type != 'librarian':
        return redirect('vehicleLending:home')

    if request.method == 'POST':
        form = VehicleForm(request.POST)
        formset = VehicleImageFormSet(request.POST, request.FILES)
        if form.is_valid() and formset.is_valid():
            vehicle = form.save(commit=False)
            vehicle.lender = request.user
            
            # Get latitude and longitude from the form
            if 'latitude' in request.POST and 'longitude' in request.POST:
                try:
                    vehicle.latitude = float(request.POST.get('latitude'))
                    vehicle.longitude = float(request.POST.get('longitude'))
                except (ValueError, TypeError):
                    # If conversion fails, attempt to geocode the location
                    if vehicle.location:
                        pass  # Geocoding will be handled by the JavaScript
            
            vehicle.save()

            if collection:
                collection.vehicles.add(vehicle)
                if collection.private_collection:
                    vehicle.private_collection = collection
                    vehicle.save()

            # save images
            images = formset.save(commit=False)
            for image in images:
                image.vehicle = vehicle
                image.save()

            return redirect(reverse('vehicleLending:details',args=[vehicle.id]))
        else:
            print(form.errors)
    else:
        form = VehicleForm()
        formset = VehicleImageFormSet()
    return render(request,'vehicleLending/add_vehicle.html', {'form': form, 'formset': formset, 'collection': collection})

def edit_vehicle(request, vehicle_id: int):
    if not request.user.is_authenticated or request.user.user_type != 'librarian':
        return redirect('vehicleLending:home')
    
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)

    if request.method == 'POST':
        form = VehicleForm(request.POST, request.FILES, instance=vehicle)
        formset = VehicleImageFormSet(request.POST, request.FILES, instance=vehicle)
        if form.is_valid() and formset.is_valid():
            vehicle = form.save(commit=False)
            
            # Get latitude and longitude from the form
            if 'latitude' in request.POST and 'longitude' in request.POST:
                try:
                    vehicle.latitude = float(request.POST.get('latitude'))
                    vehicle.longitude = float(request.POST.get('longitude'))
                except (ValueError, TypeError):
                    # If conversion fails, we'll keep the existing coordinates
                    pass
                
            vehicle.save()
            formset.save()
            return redirect(reverse('vehicleLending:details', args=[vehicle.id]))
    else:
        form = VehicleForm(instance=vehicle)
        formset = VehicleImageFormSet(instance=vehicle)
    return render(request, 'vehicleLending/add_vehicle.html', {'form': form, 'formset': formset, 'vehicle': vehicle})

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
    """
    API endpoint for search functionality. Returns vehicle and collection matches.
    This is used by the AJAX search in the navbar.
    """
    try:
        query = request.GET.get('q', '').strip()
        
        # Debug output
        print(f"Search query received: '{query}', GET params: {request.GET}")
        
        if not query:
            print("No query provided")
            return JsonResponse({'results': [{"text": "Please enter a search term", "url": "javascript:void(0)"}]})

        # Search for vehicles by make, model, or year
        vehicles = Vehicle.objects.filter(
            Q(make__icontains=query) | 
            Q(model__icontains=query) |
            Q(year__icontains=query)
        )

        for collection in Collection.objects.all():
            if collection.private_collection == True and request.user not in collection.users_with_access.all():
                vehicles = vehicles.exclude(collections=collection)

        print(f"Found {vehicles.count()} vehicles")
        vehicle_results = [{"text": f"{vehicle.make} {vehicle.model} {vehicle.year}", "url": f"/vehicle/{vehicle.id}"} for vehicle in vehicles]

        # Search for public collections by name or description
        public_collections = Collection.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query),
            private_collection=False
        )
        print(f"Found {public_collections.count()} public collections")
        public_collection_results = [{"text": f"Collection: {collection.name}", "url": f"/collection/{collection.name}"} for collection in public_collections]

        # Handle private collections based on user authentication
        private_collection_results = []
        if request.user.is_authenticated:
            if request.user.user_type == 'librarian':
                # Librarians can see all private collections
                private_collections = Collection.objects.filter(
                    Q(name__icontains=query) | 
                    Q(description__icontains=query),
                    private_collection=True
                )
            else:  # patron
                # Patrons can only see private collections they have access to
                private_collections = Collection.objects.filter(
                    Q(name__icontains=query) | 
                    Q(description__icontains=query),
                    users_with_access=request.user, 
                    private_collection=True
                )
            print(f"Found {len(private_collections)} private collections")
            private_collection_results = [{"text": f"Private Collection: {collection.name}", "url": f"/collection/{collection.name}"} for collection in private_collections]

        # Combine all results
        results = vehicle_results + public_collection_results + private_collection_results
        
        print(f"Total results: {len(results)}")
        if not results:
            results = [{"text": f"No results found for '{query}'", "url": "javascript:void(0)"}]
        elif len(results) > 10:
            results = results[:10]  # Limit to top 10 results
        
        response_data = {'results': results}
        print(f"Response data: {response_data}")
        return JsonResponse(response_data)
    except Exception as e:
        print(f"Error in search: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'error': str(e),
            'results': [{"text": "An error occurred during search", "url": "javascript:void(0)"}]
        }, status=500)
    
def collection_search_results(request):
    try:
        query = request.GET.get('q', '').strip()
        collection = request.GET.get('collection', '').strip()
        
        # Debug output
        print(f"Search query received: '{query}', GET params: {request.GET}")
        
        if not query:
            print("No query provided")
            return JsonResponse({'results': [{"text": "Please enter a search term", "url": "javascript:void(0)"}]})

        vehicles = Vehicle.objects.filter(
            Q(make__icontains=query) | 
            Q(model__icontains=query) |
            Q(year__icontains=query),
            collections__name=collection
        )

        results = [{"text": f"{vehicle.make} {vehicle.model} {vehicle.year}", "url": f"/vehicle/{vehicle.id}"} for vehicle in vehicles]

        if not results:
            results = [{"text": f"No results found for '{query}'", "url": "javascript:void(0)"}]
        elif len(results) > 10:
            results = results[:10]  # Limit to top 10 results
        
        response_data = {'results': results}
        print(f"Response data: {response_data}")
        return JsonResponse(response_data)
    except Exception as e:
        print(f"Error in search: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'error': str(e),
            'results': [{"text": "An error occurred during search", "url": "javascript:void(0)"}]
        }, status=500)


def all_vehicles(request):
    vehicles = set(Vehicle.objects.all())

    for collection in Collection.objects.all():
        for collection_vehicle in collection.vehicles.all():
            if collection_vehicle in vehicles:
                vehicles.remove(collection_vehicle)
    
    # Apply filters if they exist in the request
    vehicle_type = request.GET.get('vehicle_type')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    year_range = request.GET.get('year')
    
    # Filter by vehicle type
    if vehicle_type:
        vehicles = vehicles.filter(vehicle_type=vehicle_type)
    
    # Filter by price range
    if min_price and min_price.isdigit():
        vehicles = vehicles.filter(daily_rate__gte=int(min_price))
    if max_price and max_price.isdigit():
        vehicles = vehicles.filter(daily_rate__lte=int(max_price))
    
    # Filter by year range
    if year_range:
        if year_range == '2023+':
            vehicles = vehicles.filter(year__gte=2023)
        elif year_range == '2020-2022':
            vehicles = vehicles.filter(year__gte=2020, year__lte=2022)
        elif year_range == '2015-2019':
            vehicles = vehicles.filter(year__gte=2015, year__lte=2019)
        elif year_range == '2010-2014':
            vehicles = vehicles.filter(year__gte=2010, year__lte=2014)
        elif year_range == 'Older than 2010':
            vehicles = vehicles.filter(year__lt=2010)
    
    # Prepare filter values for the template to maintain state
    context = {
        "vehicles": vehicles,
        "filter_vehicle_type": vehicle_type or '',
        "filter_min_price": min_price or '',
        "filter_max_price": max_price or '',
        "filter_year": year_range or 'Any Year'
    }
    
    return render(request, 'vehicleLending/all_vehicles.html', context)

def map_view(request):
    vehicles = Vehicle.objects.all()
    return render(request, 'vehicleLending/map_view.html', {'vehicles': vehicles})

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
        
        if Collection.objects.filter(name=name).exists():
            messages.info(request, "A collection with this name already exists.")
            return redirect('vehicleLending:home')

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

    for vehicle in collection.vehicles.all():
        vehicle.private_collection = collection if collection.private_collection else None
        vehicle.save()

        for other_collection in vehicle.collections.all():
            if other_collection != collection:
                other_collection.vehicles.remove(vehicle)
                other_collection.save()

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
            
            # Check if user is the creator of the collection or a librarian
            if collection.creator == request.user or request.user.user_type == 'librarian':
                collection.delete()
            
        except Collection.DoesNotExist:
            pass
            
    return redirect('vehicleLending:home')

@login_required
def request_borrow(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    
    if vehicle.lender == request.user:
        messages.info(request, "You cannot request to borrow your own vehicle.")
        return redirect(reverse('vehicleLending:details', args=[vehicle_id]))
    
    if not vehicle.is_available:
        messages.info(request, "Vehicle is unavailable.")
        return redirect(reverse('vehicleLending:details', args=[vehicle_id]))
    
    borrow_request, created = BorrowRequest.objects.get_or_create(
        vehicle=vehicle,
        requester=request.user,
        lender=vehicle.lender
    )

    if not created:
        if borrow_request.status == 'pending':
            messages.info(request, "You have already requested to borrow this vehicle")
            return redirect(reverse('vehicleLending:details', args=[vehicle_id]))
        else: # status is denied; delete old request and create new borrow request
            borrow_request.delete()
            borrow_request = BorrowRequest.objects.create(
                vehicle=vehicle,
                requester=request.user,
                lender=vehicle.lender,
                status='pending'
            )
    
    return redirect('vehicleLending:requested_vehicles')

@login_required
def respond_to_request(request, request_id, response):
    borrow_request = get_object_or_404(BorrowRequest, id=request_id)

    if response == 'accept':
        if not borrow_request.vehicle.is_available:
            messages.info(request, "Vehicle currently lent. Cannot accept request at this time.")
            return redirect(reverse('vehicleLending:vehicle_requests', args=[borrow_request.vehicle.id]))
        
        borrow_request.status = 'accepted'
        borrow_request.vehicle.is_available = False
        borrow_request.vehicle.save()
    elif response == 'deny':
        borrow_request.status = 'denied'
    else:
        return redirect(reverse('vehicleLending:vehicle_requests', args=[borrow_request.vehicle.id]))
    
    borrow_request.save()
    return redirect(reverse('vehicleLending:vehicle_requests', args=[borrow_request.vehicle.id]))

@login_required
def my_vehicles(request):
    if request.user.user_type != 'librarian':
        return redirect('vehicleLending:home')

    vehicles = Vehicle.objects.filter(borrow_requests__status='pending').distinct()
    return render(request, 'vehicleLending/my_vehicles.html', {'vehicles': vehicles})

@login_required
def vehicle_requests(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)

    requests = BorrowRequest.objects.filter(vehicle=vehicle, status='pending')
    return render(request, 'vehicleLending/vehicle_requests.html', {'requests': requests})

# @login_required
# def requested_vehicles(request):
#     if not request.user.is_authenticated:
#         return redirect('vehicleLending:home')
    
#     accepted_borrow_requests = BorrowRequest.objects.filter(requester=request.user, status='accepted')
#     borrow_requests = BorrowRequest.objects.filter(requester=request.user, status__in=['pending', 'denied'])
#     return render(request, 'vehicleLending/requested_vehicles.html', {'accepted_borrow_requests': accepted_borrow_requests, 'borrow_requests': borrow_requests})

@login_required
def requested_vehicles(request):
    if not request.user.is_authenticated:
        return redirect('vehicleLending:home')

    # pull them out
    accepted = BorrowRequest.objects.filter(requester=request.user, status='accepted')
    denied   = BorrowRequest.objects.filter(requester=request.user, status='denied')
    pending  = BorrowRequest.objects.filter(requester=request.user, status='pending')

    # if any non-pending, flash an alert
    total_new = accepted.count() + denied.count()
    if total_new:
        messages.info(
            request,
            f"You have {accepted.count()} accepted "
            f"and {denied.count()} denied request(s). "
            "Check your requests below!"
        )

    return render(request, 'vehicleLending/requested_vehicles.html', {
        'accepted_borrow_requests': accepted,
        'borrow_requests': pending | denied,  # pending first, then denied
    })


@login_required
def return_vehicle(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    borrow_request = BorrowRequest.objects.filter(vehicle=vehicle, requester=request.user, status='accepted')

    if borrow_request:
        vehicle.is_available = True
        borrow_request.delete()

    vehicle.save()

    return redirect('vehicleLending:requested_vehicles')


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

def item_desc(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    user = request.user

    reviews = vehicle.reviews.select_related('reviewer').order_by('-date')

    

        
    if user.is_authenticated:
    # Check if the user already reviewed this vehicle
        existing_review = Review.objects.filter(vehicle=vehicle, reviewer=user).first()

        if request.method == 'POST':
            if existing_review:
                messages.error(request, "You have already submitted a review for this vehicle.")
                return redirect('vehicleLending:details', vehicle_id=vehicle.id)

            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.vehicle = vehicle
                review.reviewer = user
                review.save()
                messages.success(request, "Your review has been submitted.")
                return redirect('vehicleLending:details', vehicle_id=vehicle.id)
        else:
            form = ReviewForm()

        present_collections = list()
        for collection in Collection.objects.all():
            if vehicle in collection.vehicles.all() and (collection.private_collection == False or user in collection.users_with_access.all()):
                present_collections.append(collection.name)

        return render(request, 'vehicleLending/item_desc.html', {
            'vehicle': vehicle,
            'user': user,
            'form': form,
            'reviews': reviews,
            "present_collections": present_collections,
        })
    else:
        return render(request, 'vehicleLending/item_desc.html', {
            'vehicle': vehicle,
            'user': user,
            'reviews':reviews,
        })

@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    if review.reviewer != request.user:
        messages.error(request, "You can't delete someone else's review.")
        return redirect('vehicleLending:details', vehicle_id=review.vehicle.id)

    vehicle_id = review.vehicle.id
    review.delete()
    messages.success(request, "Your review has been deleted.")
    return redirect('vehicleLending:details', vehicle_id=vehicle_id)

# from django.shortcuts import get_object_or_404, redirect, render
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from .models import Collection, CollectionAccessRequest

from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Collection, CollectionAccessRequest

@login_required
def request_private_collection(request):
    # Only allow patrons (non-librarians) to submit requests.
    if request.user.user_type == "librarian":
        messages.error(request, "Librarians cannot request access—they create private collections.")
        return redirect('vehicleLending:home')
    
    if request.method == 'POST':
        collection_id = request.POST.get('collection_id')
        # Only consider private collections that are created by librarians.
        collection = get_object_or_404(
            Collection,
            id=collection_id,
            private_collection=True,
            creator__user_type="librarian"
        )
        if request.user in collection.users_with_access.all():
            messages.info(request, "You already have access to this collection.")
            return redirect('vehicleLending:home')
        
        # Check if there is already a pending request.
        existing_request = CollectionAccessRequest.objects.filter(collection=collection, requester=request.user).first()
        if existing_request is not None:
            if existing_request.status == 'pending':
                messages.info(request, "You have already requested access to this collection.")
            else: # denied request; delete existing request and create a new request
                existing_request.delete()
                CollectionAccessRequest.objects.create(collection=collection, requester=request.user)
                messages.success(request, "Your request for access has been submitted.")
        else:
            # No existing request, create a new one
            CollectionAccessRequest.objects.create(collection=collection, requester=request.user)
            messages.success(request, "Your request for access has been submitted.")
        return redirect('vehicleLending:home')
    
    else:
        # List all private collections (created by librarians)
        # that the current user does not already have access to.
        available_collections = Collection.objects.filter(private_collection=True, creator__user_type="librarian")
        collections_to_request = [c for c in available_collections if request.user not in c.users_with_access.all()]
        context = {'collections_to_request': collections_to_request}
        return render(request, 'vehicleLending/request_private_collection.html', context)


# from django.shortcuts import get_object_or_404, render, redirect
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from .models import CollectionAccessRequest

@login_required
def manage_access_requests(request):
    """
    Display all pending access requests for private collections created by the current librarian.
    """
    # Ensure only librarians can view this management page.
    if request.user.user_type != "librarian":
        messages.error(request, "Only librarians can manage collection access requests.")
        return redirect('vehicleLending:home')
    
    pending_requests = CollectionAccessRequest.objects.filter(status="pending")
    context = {"pending_requests": pending_requests}
    return render(request, "vehicleLending/manage_access_requests.html", context)

@login_required
def process_access_request(request, request_id, action):
    """
    Process a specific access request.
    Only the creator (librarian) of the collection can accept or deny a request.
    
    :param request_id: The id of the CollectionAccessRequest.
    :param action: Either 'accept' or 'deny'.
    """
    access_request = get_object_or_404(CollectionAccessRequest, id=request_id, status="pending")
    collection = access_request.collection

    # Only a librarian can process.
    if request.user.user_type != 'librarian':
        messages.error(request, "You do not have permission to process this request.")
        return redirect("vehicleLending:manage_access_requests")
    
    if action == "accept":
        # Grant access by adding the requester to the collection's users_with_access.
        collection.users_with_access.add(access_request.requester)
        access_request.status = "accepted"
        messages.success(request,
            f"Access granted to {access_request.requester.name} for {collection.name}.")
    elif action == "deny":
        access_request.status = "denied"
        messages.info(request, 
            f"Access request denied for {access_request.requester.name} on {collection.name}.")
    else:
        messages.error(request, "Invalid action.")
    access_request.save()
    return redirect("vehicleLending:manage_access_requests")


@login_required
def remove_vehicle(request):
    # Only librarians can delete vehicles
    if request.user.user_type != 'librarian':
        messages.error(request, "Only librarians may delete vehicles.")
        return redirect('vehicleLending:all')

    if request.method == 'POST':
        vehicle_id = request.POST.get('vehicle_id')
        # This will 404 if the vehicle doesn't exist or doesn't belong to you
        vehicle = get_object_or_404(Vehicle, id=vehicle_id, lender=request.user)
        vehicle.delete()
        messages.success(request, "Vehicle deleted successfully.")
    return redirect('vehicleLending:all')


# # ####-----IGNORE----_#####
# def dev_login_as_librarian(request):
#     if not settings.DEBUG:
#         return HttpResponse("Not allowed in production.")

#     librarian = User.objects.filter(user_type='librarian').first()
#     if librarian:
#         login(request, librarian)
#         return redirect('vehicleLending:promote_patron')
#     return HttpResponse("No librarian user found.")

@login_required
def add_vehicle_to_collection(request, vehicle_id: int, collection_id: int):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    collection = get_object_or_404(Collection, id=collection_id)

    if request.method == 'POST':
        collection.vehicles.add(vehicle)
        if collection.private_collection:
            vehicle.private_collection = collection
            vehicle.save()

            for other_collection in vehicle.collections.all():
                if other_collection != collection:
                    other_collection.vehicles.remove(vehicle)
                    other_collection.save()

        messages.success(request, f"Vehicle {vehicle} added to collection {collection}.")
        return redirect('vehicleLending:collection', collection_name=collection.name)

    return render(request, 'vehicleLending/add_vehicle_to_collection.html', {'vehicle': vehicle, 'collection': collection})

@login_required
def remove_vehicle_from_collection(request, vehicle_id: int, collection_id: int):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id)
    collection = get_object_or_404(Collection, id=collection_id)

    if request.method == 'POST':
        collection.vehicles.remove(vehicle)
        return redirect('vehicleLending:collection', collection_name=collection.name)

    return render(request, 'vehicleLending/remove_vehicle_from_collection.html', {'vehicle': vehicle, 'collection': collection})


