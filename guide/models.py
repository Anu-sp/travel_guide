from django.db import models
from django.contrib.auth.models import User

class District(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='district_images/images/')

    def __str__(self) :
        return self.name

class Place(models.Model):
    district = models.ForeignKey(District, related_name='places', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    distance = models.CharField(max_length=50, null=True, blank=True)
    best_time_to_visit = models.CharField(max_length=500, null=True, blank=True)
    things_to_do = models.TextField( max_length=500, null=True, blank=True)
    entry_fee = models.CharField(max_length=200, null=True, blank=True)
    timings = models.CharField(max_length=50, null=True, blank=True)
    how_to_reach = models.CharField(max_length=1000, null=True, blank=True)
    
    def __str__(self) :
        return self.name

 
class PlaceImage(models.Model):
    image = models.ImageField(upload_to='images/', verbose_name='Place Image')
    place = models.ForeignKey(Place, on_delete=models.CASCADE)

    def __str__(self):
        return f"Image for {self.place.name}"

class Feedback(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    comments = models.TextField()
    place = models.ForeignKey(Place, on_delete=models.CASCADE)  

    def __str__(self):
        return self.name

class Review(models.Model):
    place = models.ForeignKey('Place', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    rating = models.IntegerField()
    comments = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.name} for {self.place}"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    def __str__(self):
        return self.user.username




