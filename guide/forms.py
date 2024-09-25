from django import forms
from .models import Review, UserProfile
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Form for submitting reviews
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review  # Specify the model to create the form for
        fields = ['rating', 'comments', 'name', 'email']  # Fields to include in the form
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),  # Rating input as a number with a range (1-5)
            'comments': forms.Textarea(attrs={'rows': 4}),  # Text area for comments with 4 rows
        }

# Form for user signup, including profile picture upload
class SignupForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)  # Password field, with masked input
    confirm_password = forms.CharField(widget=forms.PasswordInput)  # Confirmation password field
    profile_picture = forms.ImageField(required=True)  # Profile picture field, required for the form

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password']  # Include confirm_password but exclude profile_picture as it's not part of User model

    def clean(self):
        cleaned_data = super().clean()  # Fetch cleaned data from the form
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        # Check if passwords match
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data  # Always return cleaned_data at the end of the clean method


# Signal to create a user profile when a new user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:  # Only create a profile if the user is newly created
        UserProfile.objects.create(user=instance)

# Signal to save user profile when the user object is saved
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()  # Ensure the related UserProfile instance is saved whenever the User instance is saved



