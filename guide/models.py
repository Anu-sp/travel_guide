from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Model representing a district
class District(models.Model):
    name = models.CharField(max_length=50)  # Name of the district
    image = models.ImageField(upload_to='district_images/images/')  # Image of the district

    def __str__(self):
        return self.name  # Return the district name when the object is printed

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
        return self.name  # Return the place name when the object is printed

# Model representing images associated with a place
class PlaceImage(models.Model):
    image = models.ImageField(upload_to='images/', verbose_name='Place Image')  
    place = models.ForeignKey(Place, on_delete=models.CASCADE)  

    def __str__(self):
        return f"Image for {self.place.name}"  # Return a description of the image

# Model for user feedback on a place
class Feedback(models.Model):
    name = models.CharField(max_length=100)  
    email = models.EmailField() 
    comments = models.TextField()  
    place = models.ForeignKey(Place, on_delete=models.CASCADE)  

    def __str__(self):
        return self.name  # Return the name of the feedback provider

# Model for user reviews of a place
class Review(models.Model):
    place = models.ForeignKey('Place', on_delete=models.CASCADE)  
    name = models.CharField(max_length=100) 
    email = models.EmailField()  
    rating = models.IntegerField() 
    comments = models.TextField() 
    created_at = models.DateTimeField(auto_now_add=True)  

    def __str__(self):
        return f"Review by {self.name} for {self.place}"  # Return a summary of the review

# Model for user profiles
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)  
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True) 

    def __str__(self):
        return self.user.username 

# Signal to create UserProfile when a new User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:  # Check if the User is newly created
        UserProfile.objects.create(user=instance)  # Create a corresponding UserProfile

# Signal to save UserProfile when the User object is saved
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()  # Save the UserProfile when the User is updated






