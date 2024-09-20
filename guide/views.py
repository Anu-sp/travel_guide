from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse 
from .models import District, Place, Feedback, UserProfile, Review
from .forms import FeedbackForm, ReviewForm, CustomUserCreationForm
from django.contrib.auth import authenticate, login as auth_login, logout
from django.http import JsonResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View

# Home page view
def home(request):
    profile_picture_url = None
    if request.user.is_authenticated:
        # Get the user's profile picture if authenticated
        profile_picture_url = request.user.userprofile.profile_picture.url if request.user.userprofile.profile_picture else None
    
    # Instantiate forms for login and registration
    login_form = AuthenticationForm()
    register_form = CustomUserCreationForm()  # Custom user registration form
    
    return render(request, 'guide/home.html', {
        'profile_picture_url': profile_picture_url,
        'login_form': login_form,
        'register_form': register_form,
    })

# District page view
def district_page(request):
    districts = District.objects.all()  # Retrieve all districts
    profile_picture_url = None

    if request.user.is_authenticated:
        try:
            profile = request.user.userprofile  # Access the user's profile
            profile_picture_url = profile.profile_picture.url if profile.profile_picture else None
        except UserProfile.DoesNotExist:
            profile_picture_url = None  # Handle case where profile doesn't exist

    return render(request, 'guide/district.html', {
        'districts': districts,
        'profile_picture_url': profile_picture_url,
    })

# District detail view
def district_detail(request, id):
    district = get_object_or_404(District, id=id)  # Get the district or return 404
    places = Place.objects.filter(district=district)  # Get places associated with the district
    profile_picture_url = None

    if request.user.is_authenticated:
        try:
            profile = request.user.userprofile  # Access the user's profile
            profile_picture_url = profile.profile_picture.url if profile.profile_picture else None
        except UserProfile.DoesNotExist:
            profile_picture_url = None  # Handle case where profile doesn't exist

    return render(request, 'guide/district_detail.html', {
        'district': district,
        'places': places,
        'profile_picture_url': profile_picture_url,  # Pass the profile picture URL to the template
    })

# Place detail view
def place_detail(request, id):
    place = get_object_or_404(Place, id=id)  # Get the place or return 404
    reviews = Review.objects.filter(place=place).order_by('-rating')  # Fetch and sort reviews by rating
    profile_picture_url = None

    if request.user.is_authenticated:
        try:
            profile = request.user.userprofile  # Access the user's profile
            profile_picture_url = profile.profile_picture.url if profile.profile_picture else None
        except UserProfile.DoesNotExist:
            profile_picture_url = None  # Handle case where profile doesn't exist

    return render(request, 'guide/place_detail.html', {
        'place': place,
        'reviews': reviews,
        'profile_picture_url': profile_picture_url,  # Pass the profile picture URL to the template
    })

# Feedback view for a specific place
def feedback_view(request, place_id):
    place = get_object_or_404(Place, id=place_id)  # Get the place or return 404
    
    if request.method == 'POST':
        form = FeedbackForm(request.POST)  # Create a form instance with submitted data
        if form.is_valid():
            feedback = form.save(commit=False)  # Save feedback without committing to the database yet
            feedback.place = place  # Associate feedback with the place
            feedback.save()  # Save the feedback
            return redirect('home')  # Redirect to home after saving feedback
    else:
        form = FeedbackForm()  # Create an empty form for GET requests

    return render(request, 'guide/feedback.html', {'form': form, 'place': place})

# View to display all feedbacks
def all_feedback_view(request):
    feedbacks = Feedback.objects.select_related('place').all()  # Get all feedbacks with related places
    return render(request, 'guide/all_feedback.html', {'feedbacks': feedbacks})

# Search view for places
def search_view(request):
    query = request.GET.get('q', '')  # Get search query from request
    if query:
        places = Place.objects.filter(name__icontains=query)  # Filter places by query
        suggestions = [{'id': place.id, 'name': place.name} for place in places]  # Prepare suggestions
        try:
            exact_match = Place.objects.get(name__iexact=query)  # Get exact match if it exists
            exact_match_data = {'id': exact_match.id, 'name': exact_match.name}
        except Place.DoesNotExist:
            exact_match_data = None
        
        return JsonResponse({
            'suggestions': suggestions,
            'exact_match': exact_match_data
        })

    return JsonResponse({'suggestions': [], 'exact_match': None})

# Check login status
def check_login_status(request):
    """Endpoint to check login status."""
    if request.user.is_authenticated:
        return JsonResponse({'logged_in': True})
    return JsonResponse({'logged_in': False})

# Submit a review for a specific place
@login_required
def submit_review(request, place_id):
    place = get_object_or_404(Place, id=place_id)  # Get the place or return 404
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)  # Create a form instance with submitted data
        if form.is_valid():
            review = form.save(commit=False)  # Save review without committing to the database yet
            review.place = place  # Associate review with the place
            if request.user.is_authenticated:
                review.name = request.user.username  # Set name from authenticated user
                review.email = request.user.email  # Set email from authenticated user
            review.save()  # Save the review
            return redirect('place_detail', id=place_id)  # Redirect back to place detail
    else:
        initial_data = {}
        if request.user.is_authenticated:
            # Pre-fill the form with user's name and email if logged in
            initial_data = {'name': request.user.username, 'email': request.user.email}
        form = ReviewForm(initial=initial_data)
                
    return render(request, 'guide/place_detail.html', {'form': form, 'place': place})

# Load more reviews for a specific place
def load_more_reviews(request, place_id):
    place = get_object_or_404(Place, id=place_id)  # Get the place or return 404
    reviews = place.review_set.all().order_by('rating')[3:]  # Fetch reviews, skip the first 3

    reviews_data = []
    for review in reviews:
        reviews_data.append({
            'name': review.name,
            'created_at': review.created_at.isoformat(),  # Format the created time
            'ratings': review.rating,  # Fetch rating
            'comments': review.comments,  # Fetch comments
        })

    # Check if there are more reviews to load
    has_more = place.review_set.count() > len(reviews_data) + 3 

    return JsonResponse({
        'reviews': reviews_data,
        'has_more': has_more  # Indicate if more reviews are available
    })

# User registration view
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)  # Create form instance with uploaded files
        if form.is_valid():
            user = form.save()  # Save the new user
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            
            user = authenticate(username=username, password=password)  # Authenticate the user
            
            if user is not None:
                auth_login(request, user)  # Log in the user
                messages.success(request, f'Account created successfully! Welcome, {username}')
                return redirect('home')  # Redirect to home after registration
        else:
            messages.error(request, "There was an error with your registration.")
    else:
        form = CustomUserCreationForm()  # Create an empty form for GET requests
    
    return render(request, 'guide/register.html', {'form': form})

# User profile view
@login_required
def profile_view(request):
    user = request.user
    profile_picture = None
    
    if hasattr(user, 'userprofile'):
        profile_picture = user.userprofile.profile_picture  # Get profile picture if it exists

    return render(request, 'guide/profile.html', {'profile_picture': profile_picture})

# Custom logout view
class CustomLogoutView(View):
    def post(self, request):
        logout(request)  # Log out the user
        return redirect(reverse('home'))  # Redirect to home after logging out
