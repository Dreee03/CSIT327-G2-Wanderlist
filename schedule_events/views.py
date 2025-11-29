from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from .models import Event

class EventDataView(View):
    def getEvents(self, request, *args, **kwargs):
        # 1. Fetch all events from your Supabase/PostgreSQL database
        events = Event.objects.all()

        # 2. Format the events into a list of dictionaries (JSON format)
        event_list = []
        for event in events:
            event_list.append({
                'title': event.title,
                # FullCalendar requires dates in ISO 8601 format
                'start': event.start.isoformat(), 
                'end': event.end.isoformat(),
                # You can add other properties here (e.g., 'color', 'url')
            })
        
        # 3. Return the data as a JSON response
        return JsonResponse(event_list, safe=False)