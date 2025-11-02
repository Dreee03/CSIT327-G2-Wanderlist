from django.db import models

class UserProfile(models.Model):
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(blank=True, null=True)
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', default='profile_pics/default.png', blank=True)
    
    # ✅ ADD THESE NEW FIELDS
    middle_initial = models.CharField(max_length=5, blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    bio = models.TextField(blank=True, null=True, help_text="A short bio about yourself.")

    def __str__(self):
        return self.username