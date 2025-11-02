from django.urls import path
from django.contrib.auth import views as auth_views  # ✅ FIXED: Imported from auth_views
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # Forgot Password URLs
    # ✅ FIXED: Removed indent and changed 'views.' to 'auth_views.'
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name='password_reset.html'), 
         name='password_reset'),

    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), 
         name='password_reset_done'),

    path('reset/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), 
         name='password_reset_confirm'),

    path('reset/done/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), 
         name='password_reset_complete'),
]