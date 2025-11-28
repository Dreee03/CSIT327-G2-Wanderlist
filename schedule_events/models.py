from django.db import models

class Event(models.Model):
    title = models.CharField(max_length=200)
    start = models.DateTimeField() # Note the field name 'start'
    end = models.DateTimeField()   # Note the field name 'end'
    # Add other fields like 'description', 'color', etc.
    
    def __str__(self):
        return self.title
