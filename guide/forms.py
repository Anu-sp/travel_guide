from django import forms
from .models import Review, UserProfile
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review  # Specify the model to create the form for
        fields = ['rating', 'comments', 'name', 'email']  # Fields to include in the form
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),  # Rating input as a number with a range (1-5)
            'comments': forms.Textarea(attrs={'rows': 4}),  # Text area for comments with 4 rows
        }


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


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:  # Only create a profile if the user is newly created
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()  # Ensure the related UserProfile instance is saved whenever the User instance is saved


class EditProfileForm(forms.ModelForm):
    username = forms.CharField(max_length=150, required=True)  # Username field
    email = forms.EmailField(required=True)  # Email field

    class Meta:
        model = UserProfile
        fields = ['profile_picture', 'gender', 'date_of_birth', 'phone_number']

    def __init__(self, *args, **kwargs):
        # Get the instance of UserProfile and User
        user_profile = kwargs.get('instance')
        super().__init__(*args, **kwargs)
        if user_profile:
            self.fields['username'].initial = user_profile.user.username
            self.fields['email'].initial = user_profile.user.email

    def save(self, commit=True):
        user_profile = super().save(commit=False)
        user_profile.user.username = self.cleaned_data.get('username')
        user_profile.user.email = self.cleaned_data.get('email')
        if commit:
            user_profile.save()
            user_profile.user.save()  # Save the linked User
        return user_profile

    


