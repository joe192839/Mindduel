from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

# Create a list of URLs that don't require authentication
PUBLIC_PATHS = [
    '', # home
    'accounts/login/',
    'accounts/logout/',
    'accounts/register/',  # Added register to public paths
    'quickplay/', # Make quickplay accessible to anonymous users
    'quickplay/game/',
    'quickplay/anonymous-results/',
    'quickplay/api/start-game/',
    'quickplay/api/get-question/',
    'quickplay/api/submit-answer/',
    'quickplay/api/end-game/',
    # Add new public profile endpoints
    'accounts/update-profile-photo/',
    'accounts/update-country/',
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('quickplay/', include('quickplay.urls')),
    path('accounts/', include('accounts.urls')),
    path("__reload__/", include("django_browser_reload.urls")),
]

# Serve media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # Ensure media files are served correctly
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)