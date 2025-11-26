from django.urls import path
from . import views

urlpatterns = [
    # ✅ MAIN DASHBOARD PAGE (shows Daily Quote)
    path('', views.dashboard_view, name='dashboard'),

    # ✅ PROFILE PAGE
    path('profile/', views.profile_view, name='profile'),

    # ✅ MY LISTS PAGE
    path('my-lists/', views.my_lists_view, name='my_lists'), 

    # ✅ DESTINATION ACTIONS
    path('add-destination/', views.add_destination, name='add_destination'),
    path('edit-destination/<int:destination_id>/', views.edit_destination, name='edit_destination'),
    path('delete-destination/<int:destination_id>/', views.delete_destination, name='delete_destination'),

    # ✅ REFRESH DAILY QUOTE
    path('refresh-quote/', views.refresh_quote, name='refresh_quote'),
]
