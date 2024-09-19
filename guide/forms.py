from django import forms
from .models import Feedback  
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Review

class CustomUserCreationForm(forms.ModelForm):
    profile_picture = forms.ImageField(label="Profile Picture")
    password1 = forms.CharField(widget=forms.PasswordInput())
    password2 = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'profile_picture']

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            if 'profile_picture' in self.files:
                user.profile_picture = self.files['profile_picture']
                user.save()
        return user


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['name', 'email', 'comments']  


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comments', 'name', 'email']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'comments': forms.Textarea(attrs={'rows': 4}),
        }


from .models import Profile

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['profile_picture']


