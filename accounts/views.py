# accounts/views.py
from rest_framework import status, viewsets, serializers
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action, api_view, permission_classes
from django.shortcuts import render, redirect
from django.contrib.auth import logout

from .models import CustomUser, BarberSchedule, Service, Reservation, Payment, UserCard
from .serializers import (
    CustomUserSerializer, BarberScheduleSerializer, ServiceSerializer,
    ReservationSerializer, PaymentSerializer, UserCardSerializer
)
from accounts.permissions import IsAdmin, UserPermissionsHelper

from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from dj_rest_auth.registration.views import SocialLoginView


def home(request):
    return render(request, 'home.html')

def logout_view(request):
    logout(request)
    return redirect('/')


class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter


class BarberScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = BarberScheduleSerializer
    queryset = BarberSchedule.objects.all()

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdmin()]
        return [AllowAny()]

    def list(self, request, *args, **kwargs):
        barber_id = request.query_params.get('barber_id')
        if barber_id:
            schedules = BarberSchedule.objects.filter(id_barber=barber_id)
        else:
            schedules = BarberSchedule.objects.all()
        serializer = self.get_serializer(schedules, many=True)
        return Response(serializer.data)


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def get_permissions(self):
        return UserPermissionsHelper.get_permissions(self)

    def get_queryset(self):
        queryset = super().get_queryset()
        role = self.request.query_params.get('role')
        if role is not None:
            queryset = queryset.filter(role=role)
        return queryset

    @action(detail=False, methods=['get'], url_path='me')
    def get_current_user(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    def perform_create(self, serializer):
        response = UserPermissionsHelper.perform_create(serializer, self.request)
        if response:
            return response
        serializer.save()

    def perform_update(self, serializer):
        user = self.get_object()
        if self.request.user.role != 0:
            for field in ['is_active', 'role', 'salary']:
                serializer.validated_data.pop(field, None)
        serializer.save()


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [AllowAny()]  # Cambia a [IsAdmin()] si lo deseas

    def get_queryset(self):
        category = self.request.query_params.get('category')
        if category:
            return Service.objects.filter(category=category)
        return super().get_queryset()


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

    def get_permissions(self):
        return [AllowAny()]  # Desactivado para pruebas (puedes poner IsAuthenticated)

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Reservation.objects.none()
        if user.role == 0:
            return Reservation.objects.all()
        elif user.role == 1:
            return Reservation.objects.filter(id_barber=user.id)
        elif user.role == 2:
            return Reservation.objects.filter(id_client=user.id)
        return Reservation.objects.none()

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            client = self.request.user
        else:
            client = CustomUser.objects.get(id=8)  # Cliente por defecto

        service_id = self.request.data.get('id_service')
        if not service_id:
            raise serializers.ValidationError({"id_service": "Este campo es obligatorio."})

        try:
            service = Service.objects.get(id=service_id)
        except Service.DoesNotExist:
            raise serializers.ValidationError({"id_service": "Servicio no válido."})

        serializer.save(id_client=client, id_service=service)
        print(f"✅ Reserva parcial creada con cliente {client.id} y servicio {service.id}")


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

    def get_queryset(self):
        return Payment.objects.all()


class UserCardViewSet(viewsets.ModelViewSet):
    queryset = UserCard.objects.all()
    serializer_class = UserCardSerializer

    def get_queryset(self):
        return UserCard.objects.all()


@api_view(['POST'])
def register_social_user(request):
    from django.contrib.auth.hashers import make_password

    email = request.data.get('email')
    name = request.data.get('name')
    role = 2

    if not email:
        return Response({'error': 'Falta el email'}, status=status.HTTP_400_BAD_REQUEST)

    password = make_password('firebase_login')

    user, created = CustomUser.objects.get_or_create(
        email=email,
        defaults={
            'username': email.split('@')[0],
            'first_name': name.split()[0] if name else '',
            'last_name': ' '.join(name.split()[1:]) if name and len(name.split()) > 1 else '',
            'role': role,
            'is_active': True,
            'password': password,
            'phone_number': '0000000000',
        }
    )

    if not created:
        return Response({'message': 'Usuario ya existe'}, status=status.HTTP_200_OK)

    return Response({'message': 'Usuario creado correctamente'}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([AllowAny])  # Para pruebas, cambia a IsAuthenticated luego
def user_profile(request):
    user = request.user
    return Response({
        'name': user.get_full_name() or user.username,
        'email': user.email,
        'status': 'Activo'
    })
