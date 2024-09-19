from django.shortcuts import render , get_object_or_404 , redirect
from django.urls import reverse 
from .models import District,Place,Feedback
from .forms import FeedbackForm
from django.contrib.auth import authenticate, login as auth_login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth import logout
from django.http import JsonResponse
from .forms import CustomUserCreationForm
from .models import Place, Review
from django.http import JsonResponse
from django.contrib.auth import logout as auth_logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Place, Review
from .forms import ReviewForm


def home(request):
    context = {
        'user_logged_in': request.user.is_authenticated
    }
    return render (request, 'guide/home.html')


def district_page(request):
    districts = District.objects.all()
    return render(request, 'guide/district.html', {'districts': districts})

def district_detail(request, id):
    district = get_object_or_404(District, id=id)
    places = Place.objects.filter(district=district) 
    return render(request, 'guide/district_detail.html', {'district': district, 'places': places})

def place_detail(request, id):
    place = get_object_or_404(Place, id=id)
    # Fetch and sort reviews by rating in descending order
    reviews = Review.objects.filter(place=place).order_by('-rating')
    return render(request, 'guide/place_detail.html', {'place': place, 'reviews': reviews})

def feedback_view(request, place_id):
    place = get_object_or_404(Place, id=place_id)
    
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.place = place  # Associate feedback with the place
            feedback.save()
            return redirect('home')
    else:
        form = FeedbackForm()

    return render(request, 'guide/feedback.html', {'form': form, 'place': place})


def all_feedback_view(request):
    feedbacks = Feedback.objects.select_related('place').all()
    return render(request, 'guide/all_feedback.html', {'feedbacks': feedbacks})


def search_view(request):
    query = request.GET.get('q', '')
    if query:
        # Find places with partial match
        places = Place.objects.filter(name__icontains=query)
        
        # Prepare the suggestions list for the dropdown
        suggestions = [{'id': place.id, 'name': place.name} for place in places]
        
        # Check for an exact match (case-insensitive)
        try:
            exact_match = Place.objects.get(name__iexact=query)
            exact_match_data = {'id': exact_match.id, 'name': exact_match.name}
        except Place.DoesNotExist:
            exact_match_data = None
        
        # Return both suggestions and exact match (if found)
        return JsonResponse({
            'suggestions': suggestions,
            'exact_match': exact_match_data
        })

    return JsonResponse({'suggestions': [], 'exact_match': None})


@csrf_exempt
def handle_auth(request):
    if request.method == 'POST':
        if 'application/json' in request.content_type:
            try:
                data = json.loads(request.body)
                action = data.get('action')

                if action == 'login':
                    username = data.get('username')
                    password = data.get('password')
                    user = authenticate(request, username=username, password=password)
                    if user is not None:
                        auth_login(request, user)
                        return JsonResponse({'status': 'success', 'message': 'Logged in successfully', 'redirect_url': '/district/'})
                    return JsonResponse({'status': 'error', 'message': 'Invalid credentials'})

                elif action == 'signup':
                    # Handle JSON payloads for signup if needed
                    pass

                return JsonResponse({'status': 'error', 'message': 'Invalid action'})
            except json.JSONDecodeError:
                return JsonResponse({'status': 'error', 'message': 'Invalid JSON'})
        elif 'multipart/form-data' in request.content_type:
            if request.POST:
                form = CustomUserCreationForm(request.POST, files=request.FILES)
                if form.is_valid():
                    form.save()
                    return JsonResponse({'status': 'success', 'message': 'Account created successfully'})
                else:
                    errors = form.errors.get_json_data()
                    return JsonResponse({'status': 'error', 'message': 'Error creating account', 'errors': errors})
            return JsonResponse({'status': 'error', 'message': 'Form data is missing'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Expected JSON or multipart/form-data request'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
    

def handle_logout(request):
    if request.method == 'POST':
        auth_logout(request)
        return JsonResponse({'status': 'success', 'message': 'Logged out successfully'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


def check_login_status(request):
    """Endpoint to check login status."""
    if request.user.is_authenticated:
        return JsonResponse({'logged_in': True})
    return JsonResponse({'logged_in': False})


#@login_required
def submit_review(request, place_id):
    place = get_object_or_404(Place, id=place_id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.place = place
            if request.user.is_authenticated:
                review.user = request.user
                review.name = request.user.username
                review.email = request.user.email
            review.save()
            return redirect('place_detail', id=place_id)  # Use URL name and parameter
    else:
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {'name': request.user.username, 'email': request.user.email}
        form = ReviewForm(initial=initial_data)
                
    
    return render(request, 'guide/place_detail.html', {'form': form, 'place': place})


def load_more_reviews(request, place_id):
    place = get_object_or_404(Place, id=place_id)
    reviews = place.review_set.all().order_by('ratings')[3:]  # Skip the first 3 reviews for initial display

    reviews_data = []
    for review in reviews:
        reviews_data.append({
            'name': review.name,
            'created_at': review.created_at.isoformat(),
            'ratings': review.ratings,
            'comments': review.comments,
        })

    has_more = place.review_set.count() > len(reviews_data) + 3  # Check if more reviews exist

    return JsonResponse({
        'reviews': reviews_data,
        'has_more': has_more
    })


