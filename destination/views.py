import os
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from wanderlist.supabase_client import supabase
from wanderlist import settings
import uuid 


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
        messages.error(request, f"Could not fetch destinations: {e}")

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

    # Allow either a direct URL or an uploaded file

    
    if request.method == 'POST':
        destination_image = (request.POST.get('destination_image') or '').strip()
        upload_file = request.FILES.get('destination_image')
        # If a file was uploaded, push it to Supabase Storage and build public URL
        if upload_file:
            try:
                # create a unique path inside the bucket
                filename = os.path.basename(upload_file.name)
                file_path = f"{custom_user_id}/{uuid.uuid4().hex}_{filename}"
                # Read the file content and upload the bytes
                file_content = upload_file.read()
                supabase.storage.from_('DestinationImages').upload(file_path, file_content)
                # Build public URL for the uploaded file (bucket must be public)
                destination_image = f"{settings.SUPABASE_URL}/storage/v1/object/public/DestinationImages/{file_path}"
            except Exception as e:
                messages.error(request, f'❌ Could not upload image: {e}')
                return redirect('destination:add_destination')
            
        name = (request.POST.get('name') or '').strip()
        city = (request.POST.get('city') or '').strip()
        country = (request.POST.get('country') or '').strip()
        description = (request.POST.get('description') or '').strip()
        category = (request.POST.get('category') or '').strip()
        notes = (request.POST.get('notes') or '').strip()  # ✅ Notes field
        user_id = custom_user_id  # Link destination to user
        
        # ✅ Get latitude and longitude from the form
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        

        if not name or not city or not country or not category:
            messages.error(request, 'Please fill out all required fields.')
            return redirect('destination:add_destination')
        if len(description) > 500:
                messages.error(request, 'Description must be 500 characters or fewer.')
                return redirect('destination:add_destination')
            
        # ✅ Convert coordinates to float or None
        try:
            latitude = float(latitude) if latitude else None
            longitude = float(longitude) if longitude else None
        except ValueError:
            messages.error(request, 'Latitude and Longitude must be valid numbers.')
            return redirect('destination:add_destination')

        # ✅ Check for duplicates
        try:
            existing = supabase.table('destination') \
                .select('destinationID') \
                .eq('name', name) \
                .eq('city', city) \
                .eq('country', country) \
                .execute()
            
            if existing.data:
                messages.error(request, f'This destination ({name}, {city}) already exists.')
                return redirect('destination:add_destination')
        except Exception as e:
            messages.error(request, f'Error checking for duplicates: {e}')
            return redirect('destination:add_destination')

        data = {
            'destination_image': destination_image or None,  # ✅ Save null if empty
            'name': name,
            'city': city,
            'country': country,
            'description': description or None,
            'category': category,
            'latitude': latitude,   # ✅ Save latitude
            'longitude': longitude, # ✅ Save longitude
            'notes': notes or None,  # ✅ Save null if empty
            'user_id': user_id  # Link destination to user
        }

        try:
            supabase.table('destination').insert(data).execute()
            messages.success(request, 'Destination added successfully!')
            return redirect('destination:list')
        except Exception as e:
            messages.error(request, f'Error adding destination: {e}')
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
        destination_image = (request.POST.get('destination_image') or '').strip()
        upload_file = request.FILES.get('destination_image')
        if upload_file:
            try:
                filename = os.path.basename(upload_file.name)
                file_path = f"{custom_user_id}/{uuid.uuid4().hex}_{filename}"
                # Read the file content and upload the bytes
                file_content = upload_file.read()
                supabase.storage.from_('DestinationImages').upload(file_path, file_content)
                destination_image = f"{settings.SUPABASE_URL}/storage/v1/object/public/DestinationImages/{file_path}"
            except Exception as e:
                messages.error(request, f'❌ Could not upload image: {e}')
                return render(request, 'edit_destination.html', {'destination': destination})
            
        name = (request.POST.get('name') or '').strip()
        city = (request.POST.get('city') or '').strip()
        country = (request.POST.get('country') or '').strip()
        description = (request.POST.get('description') or '').strip()
        category = (request.POST.get('category') or '').strip()
        notes = (request.POST.get('notes') or '').strip()  # ✅ Notes field
        
        # ✅ Get latitude and longitude
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')

        if not name or not city or not country or not category:
            messages.error(request, "Please fill out all required fields.")
            return render(request, 'edit_destination.html', {'destination': destination})
            
        # ✅ Convert coordinates to float or None
        try:
            latitude = float(latitude) if latitude else None
            longitude = float(longitude) if longitude else None
        except ValueError:
            messages.error(request, 'Latitude and Longitude must be valid numbers.')
            return render(request, 'edit_destination.html', {'destination': destination})

        payload = {
            'destination_image': destination_image or None,  # ✅ Update image too
            'name': name,
            'city': city,
            'country': country,
            'category': category,
            'description': description,
            'notes': notes or None,  # ✅ Update notes too
            'latitude': latitude,   # ✅ Update latitude
            'longitude': longitude, # ✅ Update longitude
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
	"""Redirect to the main dashboard page."""
	return redirect(reverse('dashboard'))
