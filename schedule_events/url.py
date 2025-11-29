from django.urls import path
from . import views

app_name = 'schedule_events'

urlpatterns = [
    path('', views.calendar_view, name='calendar'),
    path('api/events/', views.get_events_json, name='get_events'),
    path('api/events/add/', views.add_event, name='add_event'),
    path('api/events/<int:event_id>/update/', views.update_event, name='update_event'),
    path('api/events/<int:event_id>/delete/', views.delete_event, name='delete_event'),
]