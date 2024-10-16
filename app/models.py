from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class GeneralInfo(models.Model):
    company_name = models.CharField(max_length=30)
    location = models.CharField(max_length=300)
    company_logo = models.CharField(max_length=300)
    company_email = models.EmailField()
    phone = models.CharField(max_length=30)
    video_url = models.URLField(max_length= 300, null=True, blank=True)
    twitter_url = models.URLField(max_length= 300, null=True, blank=True)
    instagram_url = models.URLField(max_length= 300, null=True, blank=True)
    facebook_url = models.URLField(max_length= 300, null=True, blank=True)
    youtube_url = models.URLField(max_length= 300, null=True, blank=True)

    def __str__(self):
        return self.company_name
    

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    state = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True)
    

    def __str__(self):
        return self.user.username

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name
    
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # If you want to link it to a user
    product_name = models.CharField(max_length=255, blank=True, null=True)
    brand = models.CharField(max_length=255, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    seller = models.CharField(max_length=255, null=True, blank=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    picture = models.ImageField(upload_to='reviews/', blank=True, null=True)
    review = models.TextField()
    ip = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    status = models.BooleanField(default=True)
    stars_count = [
        (1, 'one'),
        (2, 'two'),
        (3, 'three'),
        (4, 'four'),
        (5, 'five')
    ]
    rating = models.IntegerField(choices=stars_count, default=1)

    def __str__(self):
        return f"{self.title} by {self.user.username}"
