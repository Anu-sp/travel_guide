from django.shortcuts import render , get_object_or_404 , redirect
from django.urls import reverse 
from .models import District,Place,Feedback, UserProfile,Review
from .forms import FeedbackForm,ReviewForm,CustomUserCreationForm
from django.contrib.auth import authenticate, login as auth_login,logout
from django.http import JsonResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views import View

def home(request):
    profile_picture_url = None
    if request.user.is_authenticated:
        profile_picture_url = request.user.userprofile.profile_picture.url if request.user.userprofile.profile_picture else None
    
    login_form = AuthenticationForm()
    register_form = CustomUserCreationForm()  # Use your custom form here
    
    return render(request, 'guide/home.html', {
        'profile_picture_url': profile_picture_url,
        'login_form': login_form,
        'register_form': register_form,
    })


def district_page(request):
    districts = District.objects.all()
    profile_picture_url = None

    if request.user.is_authenticated:
        try:
            profile = request.user.userprofile  # Change to userprofile
            profile_picture_url = profile.profile_picture.url if profile.profile_picture else None
        except UserProfile.DoesNotExist:
            profile_picture_url = None  # Handle the case where the profile doesn't exist

    return render(request, 'guide/district.html', {
        'districts': districts,
        'profile_picture_url': profile_picture_url,
    })


def district_detail(request, id):
    district = get_object_or_404(District, id=id)
    places = Place.objects.filter(district=district) 
    profile_picture_url = None

    if request.user.is_authenticated:
        try:
            profile = request.user.userprofile  # Access the user profile
            profile_picture_url = profile.profile_picture.url if profile.profile_picture else None
        except UserProfile.DoesNotExist:
            profile_picture_url = None  # Handle case where profile doesn't exist

    return render(request, 'guide/district_detail.html', {
        'district': district,
        'places': places,
        'profile_picture_url': profile_picture_url,  # Pass the profile picture URL to the template
    })



def place_detail(request, id):
    place = get_object_or_404(Place, id=id)
    # Fetch and sort reviews by rating in descending order
    reviews = Review.objects.filter(place=place).order_by('-rating')
    profile_picture_url = None

    if request.user.is_authenticated:
        try:
            profile = request.user.userprofile  # Access the user profile
            profile_picture_url = profile.profile_picture.url if profile.profile_picture else None
        except UserProfile.DoesNotExist:
            profile_picture_url = None  # Handle case where profile doesn't exist

    return render(request, 'guide/place_detail.html', {
        'place': place,
        'reviews': reviews,
        'profile_picture_url': profile_picture_url,  # Pass the profile picture URL to the template
    })


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
        places = Place.objects.filter(name__icontains=query)
        suggestions = [{'id': place.id, 'name': place.name} for place in places]
        try:
            exact_match = Place.objects.get(name__iexact=query)
            exact_match_data = {'id': exact_match.id, 'name': exact_match.name}
        except Place.DoesNotExist:
            exact_match_data = None
        
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


@login_required
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
            return redirect('place_detail', id=place_id)  
    else:
        initial_data = {}
        if request.user.is_authenticated:
            initial_data = {'name': request.user.username, 'email': request.user.email}
        form = ReviewForm(initial=initial_data)
                
    
    return render(request, 'guide/place_detail.html', {'form': form, 'place': place})




def load_more_reviews(request, place_id):
    place = get_object_or_404(Place, id=place_id)
    reviews = place.review_set.all().order_by('ratings')[3:]  

    reviews_data = []
    for review in reviews:
        reviews_data.append({
            'name': review.name,
            'created_at': review.created_at.isoformat(),
            'ratings': review.ratings,
            'comments': review.comments,
        })

    has_more = place.review_set.count() > len(reviews_data) + 3 

    return JsonResponse({
        'reviews': reviews_data,
        'has_more': has_more
    })



def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)  
        if form.is_valid():
            user = form.save() 
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            
           
            user = authenticate(username=username, password=password)
            
            if user is not None:
                auth_login(request, user)  
                messages.success(request, f'Account created successfully! Welcome, {username}')
                return redirect('home')  
        else:
            messages.error(request, "There was an error with your registration.")
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'guide/register.html', {'form': form})




@login_required
def profile_view(request):
    user = request.user
    profile_picture = None
    
    if hasattr(user, 'userprofile'):
        profile_picture = user.userprofile.profile_picture

    return render(request, 'guide/profile.html', {'profile_picture': profile_picture})



class CustomLogoutView(View):
    def post(self, request):
        logout(request)
        return redirect(reverse('home')) 



