from django.shortcuts import render, redirect
from accounts.forms import SupabaseUser
from .models import UserProfile
from .forms import ProfileForm
from .supabase_client import supabase
from django.contrib import messages
import json


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

    response = supabase.table("destination").select("*").execute()
    destination = response.data if response.data else []

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

    context = {
        'user': user_obj,
        'profile': profile,
        'destinations': destinations,
        'query': query,
        'category': category,
    }
    return render(request, 'dashboard.html', context)


def my_lists_view(request):
    # This view is unchanged
    if 'supabase_access_token' not in request.session:
        return redirect('login')

    username = request.session.get('logged_in_username', 'User')
    user_obj = SupabaseUser(username=username, is_authenticated=True)
    profile, _ = UserProfile.objects.get_or_create(username=username)

    try:
        response = supabase.table("destination").select("*").execute()
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
        response = supabase.table("destination").select("category, name, image_url").execute()
        
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
    """Add a new destination to Supabase."""
    if 'supabase_access_token' not in request.session:
        return redirect('login')

    # Get the current user's ID
    custom_user_id = request.session.get('custom_user_id')

    if request.method == "POST":
        name = request.POST.get("name")
        city = request.POST.get("city")
        country = request.POST.get("country")
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")
        description = request.POST.get("description")
        category = request.POST.get("category", "")
        notes = request.POST.get("notes", "")

        data = {
            "name": name,
            "city": city,
            "country": country,
            "latitude": float(latitude) if latitude else None,
            "longitude": float(longitude) if longitude else None,
            "description": description,
            "category": category,
            "notes": notes,
            "user_id": custom_user_id  # Add the user_id to the destination
        }
        try:
            supabase.table("destination").insert(data).execute()
            messages.success(request, "✅ Destination added successfully!")
        except Exception as e:
            messages.error(request, f"❌ Could not add destination: {e}")

        return redirect("dashboard")

    return render(request, "add_destination.html")


def edit_destination(request, destination_id):
    """Fetch and update a destination from Supabase."""
    if 'supabase_access_token' not in request.session:
        return redirect('login')

    # Get the current user's ID
    custom_user_id = request.session.get('custom_user_id')

    try:
        result = supabase.table('destination').select('*').eq('destinationID', destination_id).eq('user_id', custom_user_id).execute()
        destination = result.data[0] if result.data else None

        if not destination:
            messages.error(request, 'Destination not found.')
            return redirect('dashboard')
    except Exception as e:
        messages.error(request, f'Error loading destination: {e}')
        return redirect('dashboard')

    if request.method == 'POST':
        name = request.POST.get('name')
        city = request.POST.get('city')
        country = request.POST.get('country')
        description = request.POST.get('description')
        category = request.POST.get('category')
        notes = request.POST.get('notes', '')  # ✅ Handle notes in edit form

        if not name or not city or not country:
            messages.error(request, "Please fill out all required fields.")
            return render(request, 'edit_destination.html', {'destination': destination})

        payload = {
            'name': name,
            'city': city,
            'country': country,
            'category': category,
            'description': description,
            'notes': notes,  # ✅ Save updated notes
        }

        try:
            supabase.table('destination').update(payload).eq('destinationID', destination_id).eq('user_id', custom_user_id).execute()
            messages.success(request, '✅ Destination updated successfully!')
            return redirect('dashboard')
        except Exception as e:
            messages.error(request, f'❌ Could not update destination: {e}')

    return render(request, 'edit_destination.html', {'destination': destination})


def delete_destination(request, destination_id):
    """Delete a destination with confirmation."""
    if 'supabase_access_token' not in request.session:
        return redirect('login')

    # Get the current user's ID
    custom_user_id = request.session.get('custom_user_id')
    if request.method == "POST":
        try:
            supabase.table("destination").delete().eq("destinationID", destination_id).eq('user_id', custom_user_id).execute()
            messages.success(request, "🗑️ Destination deleted successfully!")
        except Exception as e:
            messages.error(request, f"❌ Could not delete destination: {e}")
    
    return redirect("dashboard")