from django.urls import path
from . import views

app_name = 'channels'

urlpatterns = [
    # Public channel pages
    path('<str:handle>/', views.ChannelDetailView.as_view(), name='detail'),
    path('<str:handle>/videos/', views.ChannelVideosView.as_view(), name='videos'),
    path('<str:handle>/playlists/', views.ChannelPlaylistsView.as_view(), name='playlists'),
    path('<str:handle>/about/', views.ChannelAboutView.as_view(), name='about'),
    path('<str:handle>/community/', views.ChannelCommunityView.as_view(), name='community'),
    
    # HTMX endpoints for channel actions
    path('<str:handle>/subscribe/', views.SubscribeToggleView.as_view(), name='subscribe_toggle'),
]