"""
URL configuration for PlayBharat project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from home.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('control-panel/', include('custom_admin.urls')),  # Custom admin dashboard
    path('', home, name='home'),
    
    # App URLs
    path('accounts/', include('accounts.urls')),
    path('videos/', include('videos.urls')),
    path('streaming/', include('streaming.urls')),
    path('search/', include('search.urls')),
    path('interactions/', include('interactions.urls')),
    path('channels/', include('channels.urls')),
    
    # Additional Pages
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
    path('contact/', TemplateView.as_view(template_name='contact.html'), name='contact'),
    
    # Legal Pages
    path('privacy/', TemplateView.as_view(template_name='privacy.html'), name='privacy'),
    path('terms/', TemplateView.as_view(template_name='terms.html'), name='terms'),
    path('copyright/', TemplateView.as_view(template_name='copyright.html'), name='copyright'),
    path('advertise/', TemplateView.as_view(template_name='advertise.html'), name='advertise'),
    
    # Support Pages
    path('help/', TemplateView.as_view(template_name='help.html'), name='help'),
    path('community-guidelines/', TemplateView.as_view(template_name='community_guidelines.html'), name='community_guidelines'),
    path('report/', TemplateView.as_view(template_name='report.html'), name='report'),
    
    # Creator Pages
    path('creator-guidelines/', TemplateView.as_view(template_name='creator_guidelines.html'), name='creator_guidelines'),
    path('monetization/', TemplateView.as_view(template_name='monetization.html'), name='monetization'),
    
    # Content Pages
    path('popular/', TemplateView.as_view(template_name='popular.html'), name='popular'),
    
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
