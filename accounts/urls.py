from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    
    # Profile management
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/edit/', views.EditProfileView.as_view(), name='edit_profile'),
    path('profile/<str:username>/', views.PublicProfileView.as_view(), name='public_profile'),
    
    # Channel management
    path('channel/create/', views.CreateChannelView.as_view(), name='create_channel'),
    path('channel/edit/', views.EditChannelView.as_view(), name='edit_channel'),
    path('channel/dashboard/', views.ChannelDashboardView.as_view(), name='channel_dashboard'),
    
    # Settings
    path('settings/', views.AccountSettingsView.as_view(), name='settings'),
    path('settings/privacy/', views.PrivacySettingsView.as_view(), name='privacy_settings'),
    path('settings/notifications/', views.NotificationSettingsView.as_view(), name='notification_settings'),
]
