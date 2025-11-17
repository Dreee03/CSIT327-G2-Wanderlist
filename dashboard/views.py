from django.shortcuts import render, redirect
from accounts.forms import SupabaseUser
import destination
from .models import UserProfile
from .forms import ProfileForm
from wanderlist.supabase_client import supabase
from django.contrib import messages
import json
import datetime


def dashboard_view(request):
    # This view is unchanged
    if 'supabase_access_token' not in request.session:
        return redirect('login')

    username = request.session.get('logged_in_username', 'User')
    user_obj = SupabaseUser(username=username, is_authenticated=True)
    custom_user_id = request.session.get('custom_user_id')

    profile, _ = UserProfile.objects.get_or_create(username=username)

    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()
    sort = request.GET.get('sort', '').strip()

    response = supabase.table("destination").select("*").eq("user_id", custom_user_id).execute()
    destinations = response.data if response.data else []

    if query:
        destinations = [
            d for d in destinations
            if query.lower() in d.get('name', '').lower()
            or query.lower() in d.get('city', '').lower()
            or query.lower() in d.get('country', '').lower()
            or query.lower() in d.get('description', '').lower()
            or query.lower() in d.get('notes', '').lower()
        ]

    if category:
        destinations = [
            d for d in destinations
            if d.get('category', '').lower() == category.lower()
        ]

    # Apply sorting if requested
    def _parse_date(d):
        # Look for common created/added timestamp fields used by Supabase
        for key in ('created_at', 'createdAt', 'inserted_at', 'date_added', 'added_at'):
            v = d.get(key)
            if v:
                try:
                    # Accept ISO format and variances (remove trailing Z -> +00:00)
                    return datetime.datetime.fromisoformat(v.replace('Z', '+00:00'))
                except Exception:
                    try:
                        return datetime.datetime.strptime(v, '%Y-%m-%d %H:%M:%S')
                    except Exception:
                        continue
        return None

    try:
        if sort == 'date_desc':
            destinations.sort(key=lambda x: _parse_date(x) or datetime.datetime.min, reverse=True)
        elif sort == 'date_asc':
            destinations.sort(key=lambda x: _parse_date(x) or datetime.datetime.min)
        elif sort == 'name_asc':
            destinations.sort(key=lambda x: (x.get('name') or '').lower())
        elif sort == 'name_desc':
            destinations.sort(key=lambda x: (x.get('name') or '').lower(), reverse=True)
    except Exception:
        # If sorting fails for any reason, silently continue with unsorted results
        pass

    context = {
        'user': user_obj,
        'profile': profile,
        'destinations': destinations,
        'query': query,
        'category': category,
        'sort': sort,
    }
    return render(request, 'dashboard.html', context)


def my_lists_view(request):
    # This view is unchanged
    if 'supabase_access_token' not in request.session:
        return redirect('login')

    username = request.session.get('logged_in_username', 'User')
    user_obj = SupabaseUser(username=username, is_authenticated=True)
    profile, _ = UserProfile.objects.get_or_create(username=username)
    custom_user_id = request.session.get('custom_user_id')

    try:
        response = supabase.table("destination").select("*").eq("user_id", custom_user_id).execute()
        destinations = response.data if response.data else []
    except Exception as e:
        destinations = []
        messages.error(request, f"Could not fetch destinations: {e}")

    context = {
        'user': user_obj,
        'profile': profile,
        'destinations_json': json.dumps(destinations),
    }
    return render(request, 'my_lists.html', context)


def profile_view(request):
    """Render an editable user profile page."""
    if 'supabase_access_token' not in request.session:
        return redirect('login')

    username = request.session.get('logged_in_username', 'User')
    user_obj = SupabaseUser(username=username, is_authenticated=True)
    custom_user_id = request.session.get('custom_user_id')

    # This will now find the profile created during registration
    profile, created = UserProfile.objects.get_or_create(username=username)
    
    # ✅ --- START: Get Destination Stats & Lists ---
    stats = {'Planned': 0, 'Visited': 0, 'Dreaming': 0, 'Total': 0}
    
    # Create lists to hold the actual destinations for the modal
    planned_destinations = []
    visited_destinations = []
    dreaming_destinations = []
    
    try:
        # Fetch the data needed for the lists
        # Note: This fetches destinations for *all* users.
        response = supabase.table("destination").select("category, name, destination_image").eq("user_id", custom_user_id).execute()
        
        if response.data:
            all_destinations = response.data
            stats['Total'] = len(all_destinations)
            
            for dest in all_destinations:
                category = dest.get('category')
                if category == 'Planned':
                    stats['Planned'] += 1
                    planned_destinations.append(dest)
                elif category == 'Visited':
                    stats['Visited'] += 1
                    visited_destinations.append(dest)
                elif category == 'Dreaming':
                    stats['Dreaming'] += 1
                    dreaming_destinations.append(dest)
    except Exception as e:
        messages.error(request, f"Could not load destination stats: {e}")
    # ✅ --- END: Get Destination Stats & Lists ---


    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)

    context = {
        'user': user_obj,
        'form': form,
        'profile': profile,
        'stats': stats, # Pass stats (counts)
        'planned_destinations': planned_destinations, # ✅ Pass lists
        'visited_destinations': visited_destinations,
        'dreaming_destinations': dreaming_destinations,
    }
    return render(request, 'profile.html', context)


# These functions are unchanged from your file
def add_destination(request):
    destination.views.add_destination(request)
    return redirect("dashboard")


def edit_destination(request, destination_id):
    destination.views.edit_destination(request, destination_id)
    return redirect("dashboard")


def delete_destination(request, destination_id):
    destination.views.delete_destination(request, destination_id)
    return redirect("dashboard")