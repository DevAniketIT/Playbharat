from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from PIL import Image


class User(AbstractUser):
    """Custom user model"""
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('hi', 'Hindi'),
        ('ta', 'Tamil'),
        ('te', 'Telugu'),
        ('bn', 'Bengali'),
        ('mr', 'Marathi'),
        ('gu', 'Gujarati'),
        ('kn', 'Kannada'),
        ('ml', 'Malayalam'),
        ('pa', 'Punjabi'),
    ]
    
    # Additional fields
    phone_number = models.CharField(max_length=15, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    preferred_language = models.CharField(
        max_length=5, 
        choices=LANGUAGE_CHOICES, 
        default='en'
    )
    country = models.CharField(max_length=100, default='India')
    state = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    
    # Verification and status
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    is_creator = models.BooleanField(default=False)
    is_verified_creator = models.BooleanField(default=False)
    
    # Privacy settings
    show_email = models.BooleanField(default=False)
    show_phone = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.username
    
    def get_absolute_url(self):
        return reverse('accounts:profile', kwargs={'username': self.username})
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # Resize profile picture if it exists
        if self.profile_picture:
            img = Image.open(self.profile_picture.path)
            if img.height > 300 or img.width > 300:
                output_size = (300, 300)
                img.thumbnail(output_size)
                img.save(self.profile_picture.path)


class Channel(models.Model):
    """Channel model"""
    CATEGORY_CHOICES = [
        ('entertainment', 'Entertainment'),
        ('music', 'Music'),
        ('education', 'Education'),
        ('news', 'News'),
        ('sports', 'Sports'),
        ('gaming', 'Gaming'),
        ('technology', 'Technology'),
        ('cooking', 'Cooking'),
        ('travel', 'Travel'),
        ('lifestyle', 'Lifestyle'),
        ('business', 'Business'),
        ('comedy', 'Comedy'),
        ('health', 'Health'),
        ('art', 'Art'),
        ('religion', 'Religion'),
        ('politics', 'Politics'),
        ('regional', 'Regional Content'),
    ]
    
    # Basic info
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='channel')
    name = models.CharField(max_length=100)
    handle = models.CharField(max_length=50, unique=True)
    description = models.TextField(max_length=1000, blank=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='entertainment')
    
    # Media
    avatar = models.ImageField(upload_to='channels/avatars/', blank=True, null=True)
    banner = models.ImageField(upload_to='channels/banners/', blank=True, null=True)
    
    # Channel stats
    subscriber_count = models.PositiveIntegerField(default=0)
    total_views = models.PositiveIntegerField(default=0)
    total_videos = models.PositiveIntegerField(default=0)
    
    # Channel settings
    is_active = models.BooleanField(default=True)
    is_monetized = models.BooleanField(default=False)
    allow_comments = models.BooleanField(default=True)
    
    # Social links
    website_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.handle})"
    
    def get_absolute_url(self):
        return reverse('channels:detail', kwargs={'handle': self.handle.replace('@', '')})
    
    def save(self, *args, **kwargs):
        # Ensure handle starts with @
        if not self.handle.startswith('@'):
            self.handle = f'@{self.handle}'
        
        super().save(*args, **kwargs)
        
        # Mark user as creator
        if not self.user.is_creator:
            self.user.is_creator = True
            self.user.save()
        
        # Resize images
        if self.avatar:
            img = Image.open(self.avatar.path)
            if img.height > 200 or img.width > 200:
                output_size = (200, 200)
                img.thumbnail(output_size)
                img.save(self.avatar.path)
        
        if self.banner:
            img = Image.open(self.banner.path)
            if img.height > 400 or img.width > 1200:
                output_size = (1200, 400)
                img.thumbnail(output_size)
                img.save(self.banner.path)
