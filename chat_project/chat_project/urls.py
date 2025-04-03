from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('chat_app.urls')),
    path('accounts/', include('django.contrib.auth.urls')),  # для login, logout, password reset
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # + статика, если нужно, но обычно collectstatic + Nginx
