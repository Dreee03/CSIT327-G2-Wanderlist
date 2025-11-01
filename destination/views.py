from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from dashboard.supabase_client import supabase


def destination_list(request):
    """Display all destinations from Supabase."""
    if 'supabase_access_token' not in request.session:
        return redirect('login')

    # Get the current user's ID
    custom_user_id = request.session.get('custom_user_id')
    try:
        # ✅ Fetch all destinations safely
        resp = supabase.table('destination').select('*').eq('user_id', custom_user_id).execute()
        destinations = resp.data if resp.data else []
    except Exception as e:
        destinations = []
        messages.error(request, f"❌ Could not fetch destinations: {e}")

    context = {'destinations': destinations}
    return render(request, 'destination.html', context)


@csrf_protect
def add_destination(request):
    """Display the Add Destination form or handle submission."""
    if request.method == 'POST':
        return create_destination(request)

    return render(request, 'add_destination.html')


@csrf_protect
@require_http_methods(["POST"])
def create_destination(request):
    """Create a new destination entry in Supabase."""
    if 'supabase_access_token' not in request.session:
        return redirect('login')

    # Get the current user's ID
    custom_user_id = request.session.get('custom_user_id')

    name = (request.POST.get('name') or '').strip()
    city = (request.POST.get('city') or '').strip()
    country = (request.POST.get('country') or '').strip()
    description = (request.POST.get('description') or '').strip()
    category = (request.POST.get('category') or '').strip()
    notes = (request.POST.get('notes') or '').strip()  # ✅ Optional notes
    user_id = custom_user_id  # Link destination to user

    # ✅ Validation
    if not name or not city or not country or not category:
        messages.error(request, 'Please fill out all required fields.')
        return redirect('destination:add_destination')

    if len(description) > 500:
        messages.error(request, 'Description must be 500 characters or fewer.')
        return redirect('destination:add_destination')

    data = {
        'name': name,
        'city': city,
        'country': country,
        'description': description,
        'category': category,
        'notes': notes or None,  # ✅ Save null if empty
        'user_id': user_id  # Link destination to user
    }

    try:
        supabase.table('destination').insert(data).execute()
        messages.success(request, '✅ Destination added successfully!')
        return redirect('destination:list')
    except Exception as e:
        messages.error(request, f'❌ Error adding destination: {e}')
        return redirect('destination:add_destination')


@csrf_protect
def edit_destination(request, destination_id):
    """Fetch and update an existing destination."""
    if 'supabase_access_token' not in request.session:
        return redirect('login')

    # Get the current user's ID
    custom_user_id = request.session.get('custom_user_id')
    try:
        result = supabase.table('destination').select('*').eq('destinationID', destination_id).eq('user_id', custom_user_id).execute()
        destination = result.data[0] if result.data else None

        if not destination:
            messages.error(request, 'Destination not found.')
            return redirect(reverse('destination:list'))
    except Exception as e:
        messages.error(request, f'❌ Error loading destination: {e}')
        return redirect(reverse('destination:list'))

    # ✅ Handle update
    if request.method == 'POST':
        name = (request.POST.get('name') or '').strip()
        city = (request.POST.get('city') or '').strip()
        country = (request.POST.get('country') or '').strip()
        description = (request.POST.get('description') or '').strip()
        category = (request.POST.get('category') or '').strip()
        notes = (request.POST.get('notes') or '').strip()  # ✅ Notes field

        if not name or not city or not country or not category:
            messages.error(request, "Please fill out all required fields.")
            return render(request, 'edit_destination.html', {'destination': destination})

        if len(description) > 500:
            messages.error(request, 'Description must be 500 characters or fewer.')
            return render(request, 'edit_destination.html', {'destination': destination})

        payload = {
            'name': name,
            'city': city,
            'country': country,
            'category': category,
            'description': description,
            'notes': notes or None,  # ✅ Update notes too
        }

        try:
            supabase.table('destination').update(payload).eq('destinationID', destination_id).eq('user_id', custom_user_id).execute()
            messages.success(request, '✅ Destination updated successfully!')
            return redirect(reverse('destination:list'))
        except Exception as e:
            messages.error(request, f'❌ Could not update destination: {e}')
            return render(request, 'edit_destination.html', {'destination': destination})

    return render(request, 'edit_destination.html', {'destination': destination})


@require_http_methods(["POST"])
def delete_destination(request, destination_id):
    """Delete a destination."""
    if 'supabase_access_token' not in request.session:
        return redirect('login')

    # Get the current user's ID
    custom_user_id = request.session.get('custom_user_id')
    try:
        supabase.table('destination').delete().eq('destinationID', destination_id).eq('user_id', custom_user_id).execute()
        messages.success(request, '🗑️ Destination deleted successfully!')
    except Exception as e:
        messages.error(request, f'❌ Could not delete destination: {e}')

    return redirect(reverse('destination:list'))


def redirect_to_dashboard(request):
    """Redirect to dashboard page."""
    return redirect(reverse('dashboard'))
