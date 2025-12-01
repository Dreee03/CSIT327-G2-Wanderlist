from django.shortcuts import render, redirect
from accounts.forms import SupabaseUser
import destination
from .models import UserProfile
from .forms import ProfileForm
from wanderlist.supabase_client import supabase
from django.contrib import messages
from django.http import JsonResponse
from .forms import ProfileForm, ChangePasswordForm
import json

# ✅ IMPORT LOGIC FROM UTILS (Clean & Modular)
from .utils import get_daily_quote, get_random_quote


# ======================================================
# ✅ AJAX ENDPOINT FOR NEW QUOTE BUTTON
# ======================================================
def refresh_quote(request):
    if request.method == "GET":
        try:
            # Logic is now handled in utils.py
            new_quote = get_random_quote()
            return JsonResponse({"quote": new_quote})
        except Exception as e:
            print(f"Error fetching quote: {e}")
            return JsonResponse({"error": "Could not fetch quote."}, status=500)


# ======================================================
# ✅ DASHBOARD
# ======================================================
def dashboard_view(request):
    if 'supabase_access_token' not in request.session:
        return redirect('login')

    username = request.session.get('logged_in_username', 'User')
    user_obj = SupabaseUser(username=username, is_authenticated=True)
    custom_user_id = request.session.get('custom_user_id')

    # Ensure profile exists locally
    profile, _ = UserProfile.objects.get_or_create(username=username)

    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()

    try:
        response = supabase.table("destination").select("*").eq("user_id", custom_user_id).execute()
        destinations = response.data if response.data else []
    except Exception as e:
        print(f"Error fetching destinations: {e}")
        destinations = []

    # SEARCH
    if query:
        destinations = [
            d for d in destinations
            if query.lower() in d.get('name', '').lower()
            or query.lower() in d.get('city', '').lower()
            or query.lower() in d.get('country', '').lower()
            or query.lower() in d.get('description', '').lower()
            or query.lower() in d.get('notes', '').lower()
        ]

    # FILTER
    if category:
        destinations = [d for d in destinations if d.get('category', '').lower() == category.lower()]

    # DAILY QUOTE (Logic handled in utils.py)
    daily_quote = get_daily_quote()

    context = {
        'user': user_obj,
        'profile': profile,
        'destinations': destinations,
        'query': query,
        'category': category,
        'quote': daily_quote
    }

    return render(request, 'dashboard.html', context)


# ======================================================
# ✅ MY LISTS
# ======================================================
def my_lists_view(request):
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


# ======================================================
# ✅ PROFILE PAGE
# ======================================================
def profile_view(request):
    if 'supabase_access_token' not in request.session:
        return redirect('login')

    username = request.session.get('logged_in_username', 'User')
    user_obj = SupabaseUser(username=username, is_authenticated=True)
    custom_user_id = request.session.get('custom_user_id')
    profile, _ = UserProfile.objects.get_or_create(username=username)

    stats = {'Planned': 0, 'Visited': 0, 'Dreaming': 0, 'Total': 0}
    planned_destinations = []
    visited_destinations = []
    dreaming_destinations = []

    try:
        response = (
            supabase.table("destination")
            .select("category, name, destination_image")
            .eq("user_id", custom_user_id)
            .execute()
        )

        if response.data:
            for dest in response.data:
                stats['Total'] += 1
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

    # FORM HANDLING
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
        'stats': stats,
        'planned_destinations': planned_destinations,
        'visited_destinations': visited_destinations,
        'dreaming_destinations': dreaming_destinations,
    }

    return render(request, 'profile.html', context)


# ======================================================
# ✅ DESTINATION CRUD (REDIRECT HANDLERS)
# ======================================================
def add_destination(request):
    destination.views.add_destination(request)
    return redirect("dashboard")


def edit_destination(request, destination_id):
    destination.views.edit_destination(request, destination_id)
    return redirect("dashboard")


def delete_destination(request, destination_id):
    destination.views.delete_destination(request, destination_id)
    return redirect("dashboard")


# ======================================================
# ✅ PASSWORD CHANGE VIEW
# ======================================================
def change_password(request):
    if request.method != 'POST':
        return redirect('profile')

    if 'supabase_access_token' not in request.session:
        return redirect('login')

    form = ChangePasswordForm(request.POST)
    
    if form.is_valid():
        new_password = form.cleaned_data['new_password']
        
        try:
            # ✅ RETRIEVE TOKENS
            access_token = request.session.get('supabase_access_token')
            refresh_token = request.session.get('supabase_refresh_token')

            # ✅ SET THE SESSION ON THE SUPABASE CLIENT
            if access_token and refresh_token:
                supabase.auth.set_session(access_token, refresh_token)
            else:
                messages.error(request, "Security tokens missing. Please logout and login again.")
                return redirect('profile')

            # Update password
            attributes = {"password": new_password}
            supabase.auth.update_user(attributes)
            messages.success(request, "Password updated successfully!")
            
        except Exception as e:
            messages.error(request, f"Failed to update password: {e}")
    else:
        messages.error(request, "Passwords do not match or are invalid.")

    return redirect('profile')