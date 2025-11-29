from django.db import models

class Event(models.Model):
    title = models.CharField(max_length=200)
    start_trip = models.DateTimeField() 
    end_trip = models.DateTimeField()   
    # Add other fields like 'description', 'color', etc.
    
    def __str__(self):
        return self.title
