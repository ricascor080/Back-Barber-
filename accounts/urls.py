from django.urls import path, include
from rest_framework.routers import DefaultRouter

from accounts.views import (
    UserViewSet, BarberScheduleViewSet,
    ServiceViewSet, ReservationViewSet,
    PaymentViewSet, UserCardViewSet,
    GoogleLogin,  # 👈 Importamos la vista personalizada para login con Google
    home, logout_view
)
from .views import user_profile
from .views import register_social_user 


router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'barber-schedules', BarberScheduleViewSet, basename='barberschedule')
router.register(r'services', ServiceViewSet)
router.register(r'reservations', ReservationViewSet)
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'cards', UserCardViewSet, basename='usercard')

urlpatterns = [
    path('', home),  # Vista HTML de prueba
    path('logout/', logout_view),  # Vista personalizada para cerrar sesión

    # API de login social con Google
    path('accounts/google/login/token/', GoogleLogin.as_view(), name='google_login_token'),
    path('usuarios/social/', register_social_user),
    path('users/me/', user_profile),

    # Rutas REST
    path('', include(router.urls)),
]

