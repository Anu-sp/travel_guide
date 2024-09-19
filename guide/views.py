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


# def home(request):
#     context = {
#         'user_logged_in': request.user.is_authenticated
#     }
#     return render (request, 'guide/home.html')

# from django.shortcuts import render
# from django.contrib.auth.decorators import login_required


# def home(request):
#     user = request.user
#     profile_picture_url = None

#     # Check if the user has a UserProfile and if it has a profile picture
#     if hasattr(user, 'userprofile'):
#         profile_picture = user.userprofile.profile_picture
#         if profile_picture:
#             profile_picture_url = profile_picture.url  # Only access the URL if the file exists

#     return render(request, 'guide/home.html', {'profile_picture_url': profile_picture_url})

from django.shortcuts import render

def home(request):
    profile_picture_url = None
    if request.user.is_authenticated:
        profile_picture_url = request.user.userprofile.profile_picture.url if request.user.userprofile.profile_picture else None
    return render(request, 'guide/home.html', {'profile_picture_url': profile_picture_url})




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


def check_login_status(request):
    """Endpoint to check login status."""
    if request.user.is_authenticated:
        return JsonResponse({'logged_in': True})
    return JsonResponse({'logged_in': False})






from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Place, Review
from .forms import ReviewForm

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


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login
from django.contrib import messages
from .forms import CustomUserCreationForm

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)  # Include files for profile picture
        if form.is_valid():
            user = form.save()  # Save the user and user profile
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            
            # Authenticate the user after registration
            user = authenticate(username=username, password=password)
            
            if user is not None:
                auth_login(request, user)  # Automatically log the user in
                messages.success(request, f'Account created successfully! Welcome, {username}')
                return redirect('home')  # Redirect to home or any other page after login
        else:
            messages.error(request, "There was an error with your registration.")
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'guide/register.html', {'form': form})


from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def profile_view(request):
    user = request.user
    profile_picture = None
    
    if hasattr(user, 'userprofile'):
        profile_picture = user.userprofile.profile_picture

    return render(request, 'guide/profile.html', {'profile_picture': profile_picture})

from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import reverse
from django.views import View

class CustomLogoutView(View):
    def post(self, request):
        logout(request)
        return redirect(reverse('home'))  # Change 'home' to your actual home URL name
