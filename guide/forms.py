from django import forms
from .models import Feedback, Review, UserProfile
from django.contrib.auth.models import User

# Form for submitting feedback
class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback  
        fields = ['name', 'email', 'comments']  # Fields to include in the form

# Form for submitting reviews
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review  # Specify the model to create the form for
        fields = ['rating', 'comments', 'name', 'email']  
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),  # Rating input as a number with a range
            'comments': forms.Textarea(attrs={'rows': 4}), 
        }

# Custom form for user registration
class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput())  
    password2 = forms.CharField(widget=forms.PasswordInput())  
    profile_picture = forms.ImageField(required=False)  # Optional profile picture field

    class Meta:
        model = User 
        fields = ['username', 'email', 'password1', 'password2', 'profile_picture']  # Fields to include in the form

    # Validate that the two password fields match
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')  
        password2 = self.cleaned_data.get('password2')  
        if password1 and password2 and password1 != password2:  # Check if they are different
            raise forms.ValidationError("Passwords don't match")  # Raise a validation error if they do not match
        return password2  # Return the valid password

    # Override the save method to handle user creation
    def save(self, commit=True):
        user = super().save(commit=False)  # Create a user object without saving to the database
        user.set_password(self.cleaned_data["password1"])  # Set the user's password
        if commit:  # If commit is True, save the user to the database
            user.save()  # Save the user
            # Create a corresponding UserProfile instance
            UserProfile.objects.create(user=user, profile_picture=self.cleaned_data.get('profile_picture'))
        return user  # Return the user instance
