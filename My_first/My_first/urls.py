from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse
from cinema.views import register_view

urlpatterns = [
    path('ping/', lambda r: HttpResponse('ok'), name='ping'),
    path('admin/', admin.site.urls),
    path('accounts/register/', register_view, name='register'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('api/', include('cinema.api_urls')),
    path('', include('cinema.urls')),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
