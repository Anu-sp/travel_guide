from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import District, Place, UserProfile, Review
from .forms import ReviewForm, SignupForm
from django.contrib.auth import authenticate, login as auth_login, logout, login
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View
from django.core.paginator import Paginator
from django.contrib.auth.models import User

# Home page view
def home(request):
    profile_picture_url = None
    if request.user.is_authenticated:
        # Fetch profile picture of authenticated user
        profile_picture_url = request.user.userprofile.profile_picture.url if request.user.userprofile.profile_picture else None
    return render(request, 'guide/home.html', {'profile_picture_url': profile_picture_url})


# District page view
def district_page(request):
    districts = District.objects.all()  # Retrieve all districts
    profile_picture_url = None
    paginator = Paginator(districts, 4)  # Pagination for displaying 4 districts per page

    page_number = request.GET.get('page')  # Get the page number from request
    districts_page = paginator.get_page(page_number)  # Get the specific page

    if request.user.is_authenticated:
        try:
            profile = request.user.userprofile  # Fetch user's profile
            profile_picture_url = profile.profile_picture.url if profile.profile_picture else None
        except UserProfile.DoesNotExist:
            profile_picture_url = None  # Handle case where profile doesn't exist

    return render(request, 'guide/district.html', {
        'districts': districts_page,  # Pass paginated districts to template
        'profile_picture_url': profile_picture_url,
    })


# District detail view
def district_detail(request, id):
    district = get_object_or_404(District, id=id)  # Retrieve specific district or return 404
    places = Place.objects.filter(district=district)  # Get places within the district
    profile_picture_url = None

    if request.user.is_authenticated:
        try:
            profile = request.user.userprofile  # Fetch user's profile
            profile_picture_url = profile.profile_picture.url if profile.profile_picture else None
        except UserProfile.DoesNotExist:
            profile_picture_url = None

    return render(request, 'guide/district_detail.html', {
        'district': district,
        'places': places,
        'profile_picture_url': profile_picture_url,
    })


# Place detail view
def place_detail(request, id):
    place = get_object_or_404(Place, id=id)  # Retrieve specific place or return 404
    reviews = Review.objects.filter(place=place).order_by('-rating')  # Fetch reviews sorted by rating
    profile_picture_url = None

    if request.user.is_authenticated:
        try:
            profile = request.user.userprofile
            profile_picture_url = profile.profile_picture.url if profile.profile_picture else None
        except UserProfile.DoesNotExist:
            profile_picture_url = None

    return render(request, 'guide/place_detail.html', {
        'place': place,
        'reviews': reviews,
        'profile_picture_url': profile_picture_url,
    })


# Submit a review for a specific place
@login_required
def submit_review(request, place_id):
    place = get_object_or_404(Place, id=place_id)  # Fetch place by ID
    if request.method == 'POST':
        form = ReviewForm(request.POST)  # Initialize review form with submitted data
        if form.is_valid():
            review = form.save(commit=False)  # Don't commit to DB yet
            review.place = place  # Assign review to the correct place
            if request.user.is_authenticated:
                review.name = request.user.username  # Use user's name if authenticated
                review.email = request.user.email  # Use user's email
            review.save()  # Save review to database
            return redirect('place_detail', id=place_id)  # Redirect to place detail page
    else:
        # Pre-fill form with user's data if authenticated
        initial_data = {'name': request.user.username, 'email': request.user.email} if request.user.is_authenticated else {}
        form = ReviewForm(initial=initial_data)

    return render(request, 'guide/place_detail.html', {'form': form, 'place': place})


# Search functionality
def search_view(request):
    query = request.GET.get('q', '').strip()  # Get query string from search form
    if query:
        places = Place.objects.filter(name__icontains=query)  # Filter places by name
        if places.exists():  # Check if any places matched the search query
            suggestions = [{'id': place.id, 'name': place.name} for place in places]
            return JsonResponse({'suggestions': suggestions})
        else:
            return JsonResponse({'suggestions': [{'id': None, 'name': 'No place found'}]})
    else:
        return HttpResponseRedirect(reverse('home'))  # Redirect to home if query is empty


# Signup functionality
def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST, request.FILES)  # Include file handling for profile pictures
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Set password
            user.save()  # Save user
            UserProfile.objects.update_or_create(  # Create/update user profile
                user=user,
                defaults={'profile_picture': form.cleaned_data.get('profile_picture')}
            )
            return redirect('login')  # Redirect to login after successful signup
    else:
        form = SignupForm()

    return render(request, 'guide/signup.html', {'form': form})


# Login functionality
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = User.objects.get(email=email)  # Fetch user by email
            user = authenticate(request, username=user.username, password=password)  # Authenticate

            if user is not None:
                login(request, user)
                return redirect('home')  # Redirect to home after login
            else:
                error_message = "Invalid email or password."
        except User.DoesNotExist:
            error_message = "Invalid email or password."

        return render(request, 'guide/login.html', {'error_message': error_message})

    return render(request, 'guide/login.html')


# Profile view with the ability to logout and update profile picture
@login_required
def profile_view(request):
    profile = request.user.userprofile

    if request.method == 'POST' and 'logout' in request.POST:
        logout(request)  # Log the user out
        return redirect('home')  # Redirect to home page after logout

    if request.method == 'POST':
        form = SignupForm(request.POST, request.FILES, instance=profile)  # Handle profile update
        if form.is_valid():
            form.save()  # Save profile updates
            return redirect('profile')  # Reload profile page
    else:
        form = SignupForm(instance=profile)  # Pre-fill form with current profile data

    return render(request, 'guide/profile.html', {'form': form})


# Logout view
class LogoutView(View):
    def post(self, request):
        logout(request)  # Log the user out
        return redirect('home')  # Redirect to home after logout
