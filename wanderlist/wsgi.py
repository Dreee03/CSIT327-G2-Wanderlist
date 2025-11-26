import os
from django.core.wsgi import get_wsgi_application

# ✅ CHANGED: 'settings' to 'wanderlist.settings'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wanderlist.settings') 

application = get_wsgi_application()