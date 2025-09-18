from django.urls import path
from . import views

app_name = 'custom_admin'

urlpatterns = [
    # Main dashboard
    path('', views.dashboard, name='dashboard'),
    
    # User management
    path('users/', views.user_management, name='user_management'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    
    # Video management
    path('videos/', views.video_management, name='video_management'),
    path('videos/<uuid:video_id>/', views.video_detail, name='video_detail'),
    
    # Channel management
    path('channels/', views.channel_management, name='channel_management'),
    path('channels/<int:channel_id>/', views.channel_detail, name='channel_detail'),
    
    # Bulk actions
    path('bulk-action/', views.bulk_action, name='bulk_action'),
]