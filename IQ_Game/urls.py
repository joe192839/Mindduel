from django.contrib import admin
from django.urls import path, include
from quiz.views import HomeView
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('quiz/', include('quiz.urls')),
    path('quickplay/', include('quickplay.urls')),
    path('accounts/login/', auth_views.LoginView.as_view(
        template_name='accounts/login.html'
    ), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(
        next_page='home'
    ), name='logout'),
    path("__reload__/", include("django_browser_reload.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)