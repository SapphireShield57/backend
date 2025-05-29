from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),

    # ✅ Include your app URLs
    path('user/', include('users.urls')),           # User endpoints (register, login, etc.)
    path('inventory/', include('inventory.urls')),  # Inventory product endpoints

    # ✅ Djoser for authentication
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]

# ✅ Serve media files in development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
