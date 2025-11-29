from django.db import models
from django.contrib.auth.models import User


class Event(models.Model):
    """Event model for storing trip events."""
    eventID = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=200)
    start_trip = models.DateTimeField() 
    end_trip = models.DateTimeField()
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['start_trip']
    
    def __str__(self):
        return f"{self.title} ({self.start_trip.date()})"
