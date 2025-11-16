from django.urls import path
from . import views

app_name = 'destination'

urlpatterns = [
    path('', views.destination_list, name='list'),
    path('back/', views.redirect_to_dashboard, name='back'),
    path('add/', views.add_destination, name='add_destination'),
    path('create/', views.create_destination, name='create'),
    path('edit/<int:destination_id>/', views.edit_destination, name='edit'),
    path('delete/<int:destination_id>/', views.delete_destination, name='delete'),
    path('explore/', views.explore, name='explore'),
    
]
