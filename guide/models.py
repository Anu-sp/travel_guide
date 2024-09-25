from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Model representing a district
class District(models.Model):
    name = models.CharField(max_length=50)  
    image = models.ImageField(upload_to='district_images/images/')  # Image for the district

    def __str__(self):
        return self.name  # Display the district's name when referenced


# Model representing a place within a district
class Place(models.Model):
    district = models.ForeignKey(District, related_name='places', on_delete=models.CASCADE)  # Link to District
    name = models.CharField(max_length=100)  
    description = models.TextField()  
    distance = models.CharField(max_length=50, null=True, blank=True)  
    best_time_to_visit = models.CharField(max_length=500, null=True, blank=True)  
    things_to_do = models.TextField(max_length=500, null=True, blank=True)
    entry_fee = models.CharField(max_length=200, null=True, blank=True)  
    timings = models.CharField(max_length=50, null=True, blank=True) 
    how_to_reach = models.CharField(max_length=1000, null=True, blank=True) 

    def __str__(self):
        return self.name  # Display the place's name when referenced


# Model representing images associated with a place
class PlaceImage(models.Model):
    image = models.ImageField(upload_to='images/', verbose_name='Place Image')  # Image of the place
    place = models.ForeignKey(Place, on_delete=models.CASCADE)  # Link to the place

    def __str__(self):
        return f"Image for {self.place.name}"  # Display image description linked to the place


# Model for user reviews of a place
class Review(models.Model):
    place = models.ForeignKey(Place, on_delete=models.CASCADE)  # Link to the place being reviewed
    name = models.CharField(max_length=100)  
    email = models.EmailField()  
    rating = models.IntegerField()  # Rating (integer value, typically between 1 and 5)
    comments = models.TextField()  # Review comments
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set the timestamp of creation

    def __str__(self):
        return f"Review by {self.name} for {self.place}"  # Display a summary of the review


# Model for user profile, extending the default Django User
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  # Link to the user
    profile_picture = models.ImageField(upload_to='profile_pics', blank=True)  # Profile picture upload, optional

    def __str__(self):
        return f"{self.user.username}"  # Display the username when referenced