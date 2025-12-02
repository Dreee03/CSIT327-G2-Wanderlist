from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse
from django.contrib import messages
from wanderlist.supabase_client import supabase
from .models import Event
import json

# ✅ ADDED IMPORTS
from dashboard.models import UserProfile
from accounts.forms import SupabaseUser

@csrf_protect
def calendar_view(request):
    """Display the FullCalendar with events."""
    if 'supabase_access_token' not in request.session:
        return redirect('login')
    
    # ✅ ADDED: Fetch User and Profile
    username = request.session.get('logged_in_username', 'User')
    user_obj = SupabaseUser(username=username, is_authenticated=True)
    profile, _ = UserProfile.objects.get_or_create(username=username)
    
    return render(request, 'schedule_events.html', {'user': user_obj, 'profile': profile})


def get_events_json(request):
    """Fetch events for the logged-in user as JSON for FullCalendar."""
    if 'supabase_access_token' not in request.session:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    custom_user_id = request.session.get('custom_user_id')
    
    try:
        # Fetch all destinations for the user that have trip dates
        response = supabase.table('destination').select(
            'destinationID, name, start_trip, end_trip, category, description'
        ).eq('user_id', custom_user_id).execute()
        
        destinations = response.data if response.data else []
        
        # Convert destinations to FullCalendar events
        events = []
        for dest in destinations:
            # Only include destinations that have both start and end dates
            if dest.get('start_trip') and dest.get('end_trip'):
                event = {
                    'id': str(dest.get('destinationID', '')),
                    'title': dest.get('name', 'Unnamed Destination'),
                    'start': dest.get('start_trip'),
                    'end': dest.get('end_trip'),
                    'category': dest.get('category', 'Dreaming'),
                    'description': dest.get('description', ''),
                    'extendedProps': {
                        'category': dest.get('category', 'Dreaming'),
                        'description': dest.get('description', ''),
                    }
                }
                
                # Set color based on category
                if dest.get('category') == 'Visited':
                    event['backgroundColor'] = '#28a745'  # Green
                    event['borderColor'] = '#20c997'
                elif dest.get('category') == 'Planned':
                    event['backgroundColor'] = '#007bff'  # Blue
                    event['borderColor'] = '#0056b3'
                else:  # Dreaming
                    event['backgroundColor'] = '#6c757d'  # Gray
                    event['borderColor'] = '#495057'
                
                events.append(event)
        
        return JsonResponse(events, safe=False)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_protect
@require_http_methods(["POST"])
def add_event(request):
    """Add a new event (via AJAX)."""
    if 'supabase_access_token' not in request.session:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    try:
        data = json.loads(request.body)
        custom_user_id = request.session.get('custom_user_id')
        
        # Create event in database
        event = Event.objects.create(
            user_id=request.user.id,
            title=data.get('title', 'Untitled Event'),
            start_trip=data.get('start'),
            end_trip=data.get('end'),
            description=data.get('description', '')
        )
        
        return JsonResponse({
            'id': event.eventID,
            'title': event.title,
            'start': event.start_trip.isoformat(),
            'end': event.end_trip.isoformat(),
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_protect
@require_http_methods(["POST"])
def update_event(request, event_id):
    """Update an existing event (via AJAX)."""
    if 'supabase_access_token' not in request.session:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    try:
        data = json.loads(request.body)
        event = Event.objects.get(eventID=event_id, user=request.user)
        
        event.title = data.get('title', event.title)
        event.start_trip = data.get('start', event.start_trip)
        event.end_trip = data.get('end', event.end_trip)
        event.description = data.get('description', event.description)
        event.save()
        
        return JsonResponse({'success': True})
    except Event.DoesNotExist:
        return JsonResponse({'error': 'Event not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@csrf_protect
@require_http_methods(["POST"])
def delete_event(request, event_id):
    """Delete an event (via AJAX)."""
    if 'supabase_access_token' not in request.session:
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    try:
        event = Event.objects.get(eventID=event_id, user=request.user)
        event.delete()
        return JsonResponse({'success': True})
    except Event.DoesNotExist:
        return JsonResponse({'error': 'Event not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)