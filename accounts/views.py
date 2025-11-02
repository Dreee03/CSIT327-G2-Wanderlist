from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm, CustomAuthenticationForm, SupabaseUser
from wanderlist.utils import register_user, login_user

# Import the Django UserProfile model
from dashboard.models import UserProfile


def home(request):
    # This view is unchanged
    if 'supabase_access_token' in request.session:
        username = request.session.get('logged_in_username', 'User') 
        user_obj = SupabaseUser(username=username, is_authenticated=True)
    else:
        user_obj = SupabaseUser(username='Guest', is_authenticated=False)
    
    context = {'user': user_obj}
    return render(request, 'home.html', context)

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            # ✅ Get fields from form (middle_initial removed)
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            age = form.cleaned_data.get('age')

            try:
                # ✅ Pass new fields to register_user (middle_initial removed)
                result = register_user(
                    email, password, username, 
                    first_name, last_name, age
                )
            except Exception:
                messages.error(request, 'Registration service is temporarily unavailable. Please try again later.')
                return render(request, 'register.html', {'form': form})

            if result.get('success'):
                # ✅ Create the local Django UserProfile (middle_initial removed)
                UserProfile.objects.create(
                    username=username,
                    email=email,
                    first_name=first_name,
                    last_name=last_name,
                    age=age
                )
                messages.success(request, 'Registration successful. Please check your email to confirm your account.')
                return redirect('login')
            else:
                safe_message = result.get('message') or 'Registration failed. Please verify your details and try again.'
                messages.error(request, safe_message)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    # This view is unchanged
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            
            try:
                session_result = login_user(username, password)
            except Exception:
                messages.error(request, 'Login service is temporarily unavailable. Please try again later.')
                return render(request, 'login.html', {'form': form})
            
            if session_result.get('success'):
                request.session['supabase_access_token'] = session_result['token']
                request.session['supabase_auth_id'] = session_result['supabase_auth_id']
                request.session['custom_user_id'] = session_result['custom_user_id'] 
                request.session['logged_in_username'] = session_result['username'] 
                messages.success(request, f"Welcome back, {username}!")
                return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, "Please enter a valid username and password.")
    else:
        form = CustomAuthenticationForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    # This view is unchanged
    from wanderlist.utils import supabase_sign_out
    
    supabase_sign_out() 
    
    if 'supabase_access_token' in request.session:
        del request.session['supabase_access_token']
    if 'supabase_auth_id' in request.session:
        del request.session['supabase_auth_id']
    if 'custom_user_id' in request.session:
        del request.session['custom_user_id']
    if 'logged_in_username' in request.session:
        del request.session['logged_in_username']
        
    messages.info(request, "You have been logged out.")
    return redirect('login')