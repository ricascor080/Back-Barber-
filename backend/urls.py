from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView  # ← AÑADE ESTO


urlpatterns = [
    path("accounts/", include("allauth.urls")),
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('emails/', include('emails.urls')),

    # 🔐 Rutas para login con JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),     # ← Login
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),     # ← Refrescar token
    
]
