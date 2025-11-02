from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from dashboard.supabase_client import supabase
import uuid 


def destination_list(request):
<<<<<<< HEAD
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

=======
	"""Display the list of destinations and the create/edit form."""
	try:
		resp = supabase.table('destination').select('*').execute()
		destinations = resp.data if resp.data else []
	except Exception as e:
		destinations = []
		messages.error(request, f"Could not fetch destinations: {e}")

	context = {
		'destinations': destinations,
	}
	return render(request, 'destination.html', context)
>>>>>>> 74af7ebeecfbf5bdbc34dfa069def25e5bb2869b

@csrf_protect
def add_destination(request):
    """Display the Add Destination form or handle submission."""
    if request.method == 'POST':
        return create_destination(request)

    return render(request, 'add_destination.html')


@csrf_protect
@require_http_methods(["POST"])
def create_destination(request):
<<<<<<< HEAD
    """Create a new destination entry in Supabase."""
    if 'supabase_access_token' not in request.session:
        return redirect('login')

    # Get the current user's ID
    custom_user_id = request.session.get('custom_user_id')

    # Allow either a direct URL or an uploaded file
    destination_image = (request.POST.get('destination_image') or '').strip()
    upload_file = request.FILES.get('destination_image')
    # If a file was uploaded, push it to Supabase Storage and build public URL
    if upload_file:
        try:
            # create a unique path inside the bucket
            filename = os.path.basename(upload_file.name)
            file_path = f"{custom_user_id}/{uuid4().hex}_{filename}"
            # upload expects a file-like object; UploadedFile.file works
            supabase.storage.from_('DestinationImages').upload(file_path, upload_file.file)
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
    notes = (request.POST.get('notes') or '').strip()  # ✅ Optional notes
    user_id = custom_user_id  # Link destination to user

    # ✅ Validation
    if not name or not city or not country or not category:
        messages.error(request, 'Please fill out all required fields.')
        return redirect('destination:add_destination')
=======
    if request.method == 'POST':
        name = (request.POST.get('name') or '').strip()
        city = (request.POST.get('city') or '').strip()
        country = (request.POST.get('country') or '').strip()
        description = (request.POST.get('description') or '').strip()
        category = (request.POST.get('category') or '').strip()
        
        # ✅ Get latitude and longitude from the form
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        
        image_file = request.FILES.get('image')
        image_url = None

        if not name or not city or not country or not category:
            messages.error(request, 'Please fill out all required fields.')
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

        if image_file:
            if image_file.size > 20 * 1024 * 1024: 
                messages.error(request, 'Image file is too large (max 20MB).') 
                return redirect('destination:add_destination')
            
            try:
                file_ext = image_file.name.split('.')[-1]
                file_path = f"public/{uuid.uuid4()}.{file_ext}"
                supabase.storage.from_("destination_images").upload(
                    file_path, image_file.read(), {"content-type": image_file.content_type}
                )
                image_url = supabase.storage.from_("destination_images").get_public_url(file_path)
            except Exception as e:
                messages.error(request, f'Error uploading image: {e}')
                return redirect('destination:add_destination')

        data = {
            'name': name,
            'city': city,
            'country': country,
            'description': description,
            'category': category,
            'image_url': image_url, 
            'latitude': latitude,   # ✅ Save latitude
            'longitude': longitude, # ✅ Save longitude
        }

        try:
            supabase.table('destination').insert(data).execute()
            messages.success(request, 'Destination added successfully!')
            return redirect('destination:list')
        except Exception as e:
            messages.error(request, f'Error adding destination: {e}')
            return redirect('destination:add_destination')

    return render(request, 'add_destination.html')
>>>>>>> 74af7ebeecfbf5bdbc34dfa069def25e5bb2869b

    if len(description) > 500:
        messages.error(request, 'Description must be 500 characters or fewer.')
        return redirect('destination:add_destination')

<<<<<<< HEAD
    data = {
        'destination_image': destination_image or None,  # ✅ Save null if empty
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


=======
>>>>>>> 74af7ebeecfbf5bdbc34dfa069def25e5bb2869b
@csrf_protect
def edit_destination(request, destination_id):
    """Fetch and update an existing destination."""
    if 'supabase_access_token' not in request.session:
        return redirect('login')

    # Get the current user's ID
    custom_user_id = request.session.get('custom_user_id')
    try:
<<<<<<< HEAD
        result = supabase.table('destination').select('*').eq('destinationID', destination_id).eq('user_id', custom_user_id).execute()
=======
        result = supabase.table('destination').select('*').eq('destinationID', destination_id).execute()
>>>>>>> 74af7ebeecfbf5bdbc34dfa069def25e5bb2869b
        destination = result.data[0] if result.data else None

        if not destination:
            messages.error(request, 'Destination not found.')
            return redirect(reverse('destination:list'))
    except Exception as e:
        messages.error(request, f'❌ Error loading destination: {e}')
        return redirect(reverse('destination:list'))

<<<<<<< HEAD
    # ✅ Handle update
=======
>>>>>>> 74af7ebeecfbf5bdbc34dfa069def25e5bb2869b
    if request.method == 'POST':
        destination_image = (request.POST.get('destination_image') or '').strip()
        upload_file = request.FILES.get('destination_image')
        if upload_file:
            try:
                filename = os.path.basename(upload_file.name)
                file_path = f"{custom_user_id}/{uuid4().hex}_{filename}"
                supabase.storage.from_('DestinationImages').upload(file_path, upload_file.file)
                destination_image = f"{settings.SUPABASE_URL}/storage/v1/object/public/DestinationImages/{file_path}"
            except Exception as e:
                messages.error(request, f'❌ Could not upload image: {e}')
                return render(request, 'edit_destination.html', {'destination': destination})
        name = (request.POST.get('name') or '').strip()
        city = (request.POST.get('city') or '').strip()
        country = (request.POST.get('country') or '').strip()
        description = (request.POST.get('description') or '').strip()
        category = (request.POST.get('category') or '').strip()
<<<<<<< HEAD
        notes = (request.POST.get('notes') or '').strip()  # ✅ Notes field
=======
        
        # ✅ Get latitude and longitude
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        
        image_file = request.FILES.get('image')
        image_url = destination.get('image_url') 
>>>>>>> 74af7ebeecfbf5bdbc34dfa069def25e5bb2869b

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

        if image_file:
            if image_file.size > 20 * 1024 * 1024: 
                messages.error(request, 'Image file is too large (max 20MB).') 
                return render(request, 'edit_destination.html', {'destination': destination})
            
            try:
                file_ext = image_file.name.split('.')[-1]
                file_path = f"public/{uuid.uuid4()}.{file_ext}"
                supabase.storage.from_("destination_images").upload(
                    file_path, image_file.read(), {"content-type": image_file.content_type}
                )
                image_url = supabase.storage.from_("destination_images").get_public_url(file_path)
            except Exception as e:
                messages.error(request, f'Error uploading image: {e}')
                return render(request, 'edit_destination.html', {'destination': destination})

        payload = {
            'destination_image': destination_image or None,  # ✅ Update image too
            'name': name,
            'city': city,
            'country': country,
            'category': category,
            'description': description,
<<<<<<< HEAD
            'notes': notes or None,  # ✅ Update notes too
=======
            'image_url': image_url, 
            'latitude': latitude,   # ✅ Update latitude
            'longitude': longitude, # ✅ Update longitude
>>>>>>> 74af7ebeecfbf5bdbc34dfa069def25e5bb2869b
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
<<<<<<< HEAD
    """Redirect to dashboard page."""
    return redirect(reverse('dashboard'))
=======
	"""Redirect to the main dashboard page."""
	return redirect(reverse('dashboard'))
>>>>>>> 74af7ebeecfbf5bdbc34dfa069def25e5bb2869b
