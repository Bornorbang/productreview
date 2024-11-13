from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
import uuid

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
    image_url = models.URLField(blank=True, null=True)  # For displaying category images

    def __str__(self):
        return self.name

    def review_count(self):
        """Returns the number of reviews in this category."""
        return self.reviews.count()  # Uses the related_name in the Review model
    


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=255, blank=True, null=True)
    brand = models.CharField(max_length=255, blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='reviews')  # Added related_name
    seller = models.CharField(max_length=255, blank=True, null=True)
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
    
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    content = models.TextField(max_length= 500, null=True, blank=True)
    review = models.ForeignKey(Review, related_name='comments', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"comment by {self.user} on {self.review}"
    



class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(default=now)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver}"


class Room(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"Room - {self.name}"


class Roommessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.CharField(max_length=1000)
    date = models.DateTimeField(auto_now=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)

    def __str__(self):
        return f"Message from {self.user} | {self.date}"
    
class PasswordReset(models.Model):
    user =  models.ForeignKey(User, on_delete=models.CASCADE)
    reset_id = models. UUIDField(default = uuid.uuid4, unique = True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Password reset for {self.user.username} at {self.created_at}"
    
class Newsletter(models.Model):
    email =  models.EmailField(max_length=254, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)