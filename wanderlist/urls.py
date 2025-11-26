from django.contrib import admin
from django.urls import path, include, re_path
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

# Redirect root URL to dashboard
def home_redirect(request):
    return redirect('dashboard')  # Redirect '/' to '/dashboard/'

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # App URLs
    path('accounts/', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),  # Dashboard and daily quote live here
    path('destination/', include('destination.urls')),
    
    # Root redirect
    path('', home_redirect),
]

# Serve media files during development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Ensure media files are reachable even if DEBUG=False (for local/dev)
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
