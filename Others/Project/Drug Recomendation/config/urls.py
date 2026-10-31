"""
URL configuration for AI-Based Drug Recommendation System.
"""

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static


def home_view(request):
    if request.user.is_authenticated:
        return redirect('accounts:role_redirect')
    return redirect('accounts:login')


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('accounts/', include('accounts.urls')),
    path('symptoms/', include('symptoms.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('reports/', include('reports.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    if settings.STATICFILES_DIRS:
        urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    else:
        urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
