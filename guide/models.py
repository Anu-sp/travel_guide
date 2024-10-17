from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.core.exceptions import ValidationError

def generate_unique_slug(instance, slug):
    unique_slug = slug
    num = 1
    while District.objects.filter(slug=unique_slug).exists():
        unique_slug = f"{slug}-{num}"
        num += 1
    return unique_slug


class District(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='district_images/images/')  # Image for the district
    slug = models.SlugField(max_length=60, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            slug = slugify(self.name)
            self.slug = generate_unique_slug(self, slug)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name  # Display the district's name when referenced


class Place(models.Model):
    district = models.ForeignKey(District, related_name='places', on_delete=models.CASCADE)  # Link to District
    name = models.CharField(max_length=100)
    description = models.TextField()
    distance = models.CharField(max_length=50, null=True, blank=True)
    best_time_to_visit = models.CharField(max_length=500, null=True, blank=True)
    things_to_do = models.TextField(null=True, blank=True)  # Removed max_length for TextField
    entry_fee = models.CharField(max_length=200, null=True, blank=True)
    timings = models.CharField(max_length=50, null=True, blank=True)
    how_to_reach = models.CharField(max_length=1000, null=True, blank=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            slug = slugify(self.name)
            self.slug = generate_unique_slug(self, slug)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name  # Display the place's name when referenced


class PlaceImage(models.Model):
    image = models.ImageField(upload_to='images/', verbose_name='Place Image')  # Image of the place
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='images')  # Link to the place

    def __str__(self):
        return f"Image for {self.place.name}"  # Display image description linked to the place


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link to the user
    place = models.ForeignKey(Place, on_delete=models.CASCADE)  # Link to the place being reviewed
    name = models.CharField(max_length=100)  
    email = models.EmailField()  
    rating = models.IntegerField()  # Rating (integer value, typically between 1 and 5)
    comments = models.TextField()  # Review comments
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set the timestamp of creation

    def clean(self):
        if not (1 <= self.rating <= 5):
            raise ValidationError('Rating must be between 1 and 5.')

    def __str__(self):
        return f"Review by {self.name} for {self.place}"  # Display a summary of the review


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link to the user
    profile_picture = models.ImageField(upload_to='profile_pics', blank=True)  # Profile picture upload, optional

    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}"  # Display the username when referenced
