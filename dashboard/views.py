from django.shortcuts import render, redirect
from accounts.forms import SupabaseUser
from .models import UserProfile
from .forms import ProfileForm
from wanderlist.supabase_client import supabase
from django.contrib import messages
import json


def dashboard_view(request):
    """Render the dashboard.html with destinations + search & filter."""
    if 'supabase_access_token' not in request.session:
        return redirect('login')

    username = request.session.get('logged_in_username', 'User')
    user_obj = SupabaseUser(username=username, is_authenticated=True)
    custom_user_id = request.session.get('custom_user_id')

    # Retrieve or create profile record so navbar shows profile picture
    profile, _ = UserProfile.objects.get_or_create(username=username)

    # --- NEW: Get search and filter parameters ---
    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()

    try:
        # Fetch destinations filtered by user_id
        response = supabase.table("destination").select("*").eq("user_id", custom_user_id).execute()
        destinations = response.data if response.data else []
    except Exception as e:
        destinations = []
        messages.error(request, f"❌ Could not fetch destinations: {e}")

    # --- Apply local filtering ---
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
    """Render a Leaflet map with all destinations."""
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
    profile, _ = UserProfile.objects.get_or_create(username=username)

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
    }
    return render(request, 'profile.html', context)


# ✅ ADD DESTINATION
def add_destination(request):
    """Add a new destination to Supabase."""
    if 'supabase_access_token' not in request.session:
        return redirect('login')

    # Get the current user's ID
    custom_user_id = request.session.get('custom_user_id')

    if request.method == "POST":
        destination_image = (request.POST.get("destination_image") or "").strip()
        name = request.POST.get("name")
        city = request.POST.get("city")
        country = request.POST.get("country")
        latitude = request.POST.get("latitude")
        longitude = request.POST.get("longitude")
        description = request.POST.get("description")
        category = request.POST.get("category", "")
        notes = request.POST.get("notes", "")

        data = {
            "destination_image": destination_image or None,  # Save null if empty
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


# ✅ EDIT DESTINATION
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
        destination_image = (request.POST.get('destination_image') or '').strip()
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
            'destination_image': destination_image or None,  # ✅ Update image too
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


# ✅ DELETE DESTINATION
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
