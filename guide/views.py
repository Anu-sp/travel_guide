from django.views import View
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import District, Place, UserProfile, Review
from .forms import ReviewForm, SignupForm
from django.contrib.auth import authenticate, logout, login
from django.http import JsonResponse, HttpResponseRedirect,HttpResponseForbidden, HttpResponseNotFound
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth.models import User
from .forms import EditProfileForm
from django.contrib import messages


def home(request):
    profile_picture_url = None
    if request.user.is_authenticated:
        # Fetch profile picture of authenticated user
        profile_picture_url = request.user.userprofile.profile_picture.url if request.user.userprofile.profile_picture else None
    return render(request, 'guide/home.html', {'profile_picture_url': profile_picture_url})


def district_page(request):
    districts = District.objects.all() # Retrieve all districts
    profile_picture_url = None
    paginator = Paginator(districts, 4)  # Pagination for displaying 4 districts per page

    page_number = request.GET.get('page', 1)  # Get the page number from request (default to 1)
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



def district_detail(request, slug):
    district = get_object_or_404(District, slug=slug)  # Retrieve specific district or return 404
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
 


def place_detail(request, slug):
    place = get_object_or_404(Place, slug=slug )  # Retrieve specific place or return 404
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




def search_view(request):
    query = request.GET.get('q', '').strip()  # Get query string from search form
    print(f"Search query: '{query}'")  # Debug line
    if query:
        places = Place.objects.filter(name__icontains=query) # Filter places by name
        print(f"Found places: {[place.name for place in places]}")  # Debug line
        if places.exists():  # Check if any places matched the search query
            suggestions = [{'slug': place.slug, 'name': place.name} for place in places]
            return JsonResponse({'suggestions': suggestions})
        else:
            return JsonResponse({'suggestions': [{'slug': None, 'name': 'No place found'}]})
    else:
        return HttpResponseRedirect(reverse('home'))  # Redirect to home if query is empty




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




@login_required
def profile_view(request):
    # Ensure a UserProfile exists for the logged-in user
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    # Handle logout action
    if request.method == 'POST' and 'logout' in request.POST:
        logout(request)
        return redirect('home')  # Redirect to the home page after logout

    # Handle profile update
    if request.method == 'POST':
        form = SignupForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()  # Save profile updates
            return redirect('profile')  # Reload profile page
    else:
        form = SignupForm(instance=profile)  # Pre-fill form with current profile data

    return render(request, 'guide/profile.html', {'form': form})
  

@login_required
def edit_profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = EditProfileForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            # After saving, reload the updated user profile
            return redirect('home')   # Redirect to the profile page after successful update
    else:
        form = EditProfileForm(instance=user_profile)

    # Pass user information to the template
    context = {
        'form': form,
        'user': request.user,  # Pass the current user info
        'profile': user_profile  # Optional: Pass additional profile info
    }

    return render(request, 'guide/edit_profile.html', context)



def delete_review(request, review_id):
    # Ensure that the request is a POST request
    if request.method == 'POST':
        # Get the review or return a 404 error if it does not exist
        review = get_object_or_404(Review, id=review_id)

        # Check if the logged-in user is the owner of the review
        if review.user != request.user:
            return HttpResponseForbidden("You are not allowed to delete this review.")

        # Get the slug of the place associated with the review
        place_slug = review.place.slug  # Assuming review has a ForeignKey to Place

        # Delete the review if the user is authorized
        review.delete()

        # Redirect to the place detail page using the slug
        return redirect('place_detail', slug=place_slug)  # Corrected to use slug

    return HttpResponseNotFound("Invalid request method.")


@login_required
def submit_review(request, place_slug):
    place = get_object_or_404(Place, slug=place_slug)  # Fetch place by ID
    if request.method == 'POST':
        review_id = request.POST.get('reviewId')  # Get the review ID from the form
        if review_id:
            review = get_object_or_404(Review, id=review_id, user=request.user)  # Fetch the existing review
            form = ReviewForm(request.POST, instance=review)  # Bind the form to the existing review
        else:
            form = ReviewForm(request.POST)  # Initialize a new review form
        
        if form.is_valid():
            review = form.save(commit=False)  # Don't commit to DB yet
            review.place = place  # Assign review to the correct place
            review.user = request.user 
            if request.user.is_authenticated:
                review.name = request.user.username  # Use user's name if authenticated
                review.email = request.user.email  # Use user's email
            review.save()  # Save review to database
            return redirect('place_detail', slug=place_slug)  # Redirect to place detail page
    else:
        # Pre-fill form with user's data if authenticated
        initial_data = {'name': request.user.username, 'email': request.user.email} if request.user.is_authenticated else {}
        form = ReviewForm(initial=initial_data)

    return render(request, 'guide/place_detail.html', {'form': form, 'place': place})


def login_view(request):
    # Capture the 'next' parameter if it exists
    next_url = request.GET.get('next', 'home')  # Default to 'home' if 'next' is not provided

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            # Fetch user by email
            user_obj = User.objects.get(email=email)
            user = authenticate(request, username=user_obj.username, password=password)  # Authenticate

            if user is not None:
                login(request, user)  # Log the user in
                # Redirect to the 'next' URL or home if no 'next' is provided
                return redirect(next_url)
            else:
                messages.error(request, "Invalid email or password.")
        except User.DoesNotExist:
            messages.error(request, "Invalid email or password.")

    # Re-render login page, pass the 'next' URL in the context to preserve it
    return render(request, 'guide/login.html', {'next': next_url})

























