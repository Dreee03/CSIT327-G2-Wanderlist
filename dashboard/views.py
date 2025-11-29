from django.shortcuts import render, redirect
from accounts.forms import SupabaseUser
import destination
from .models import UserProfile
from .forms import ProfileForm
from wanderlist.supabase_client import supabase
from django.contrib import messages
from django.http import JsonResponse
import json
import datetime
import hashlib
import random

# ======================================================
# ✅ DAILY QUOTES
# ======================================================
QUOTES = [
    "Travel far enough, you meet yourself.",
    "Not all who wander are lost.",
    "Jobs fill your pocket, adventures fill your soul.",
    "Life is short. Travel often.",
    "Wherever you go becomes part of you.",
    "Adventure is worthwhile.",
    "Collect moments, not things.",
    "Wander often, wonder always.",
    "Traveling – it leaves you speechless, then turns you into a storyteller.",
    "The world is a book, and those who do not travel read only one page.",
    "Adventure may hurt you but monotony will kill you.",
    "Life is short and the world is wide.",
    "Better to see something once than hear about it a thousand times.",
    "Take only memories, leave only footprints.",
    "A journey of a thousand miles begins with a single step."
]


def get_daily_quote():
    """Returns a deterministic quote for the current day."""
    today = datetime.date.today().isoformat()
    hash_value = int(hashlib.md5(today.encode()).hexdigest(), 16)
    index = hash_value % len(QUOTES)
    return QUOTES[index]


def get_random_quote():
    """Returns a random quote for refresh button."""
    return random.choice(QUOTES)


# ======================================================
# ✅ AJAX ENDPOINT FOR NEW QUOTE BUTTON
# ======================================================
def refresh_quote(request):
    if request.method == "GET":
        try:
            new_quote = get_random_quote()
            return JsonResponse({"quote": new_quote})
        except Exception:
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

    # FIXED SPELLING ERROR
    profile, _ = UserProfile.objects.get_or_create(username=username)

    query = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()

    response = supabase.table("destination").select("*").eq("user_id", custom_user_id).execute()
    destinations = response.data if response.data else []

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

    # DAILY QUOTE
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
