from django.contrib import admin
from django.urls import path, include
from users.views import health_check 

urlpatterns = [
    path('health/', health_check),
    path('admin/', admin.site.urls),
    path("users/", include("users.urls")),
    path("company/", include("companies.urls")),
    path('api/', include('packages.urls')),
    path('user/', include('bookings.urls')),
    path("api/", include("notifications.urls")),
    path("api/", include("admin.urls")),
     path("api/chat/", include("chat.urls")),
]
