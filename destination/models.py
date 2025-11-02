from django.db import models
from django.contrib.auth.models import User

class Destination(models.Model):
    CATEGORY_CHOICES = [
        ('Planned', 'Planned'),
        ('Visited', 'Visited'),
        ('Dreaming', 'Dreaming'),
    ]

    destinationID = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='destinations')
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='Dreaming')
    image_url = models.URLField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)  # ✅ Notes / Journal Entry
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.category})"
