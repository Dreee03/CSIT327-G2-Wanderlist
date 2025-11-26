from django.contrib import admin
from django.urls import path, include, re_path
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

def home_redirect(request):
    return redirect('dashboard')  # ✅ Redirect to dashboard instead of 'home'

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('accounts/', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),  # ✅ Quote will show here
    path('destination/', include('destination.urls')),
    
    path('', home_redirect),
]

# ✅ Serve media files
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
