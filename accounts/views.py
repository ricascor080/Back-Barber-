# accounts/views.py
from rest_framework import status, viewsets, serializers
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action, api_view, permission_classes
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.hashers import make_password

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
            return [AllowAny()]
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

    @action(detail=False, methods=['get', 'patch'], url_path='me')
    def me(self, request):
     if request.method == 'GET':
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

     elif request.method == 'PATCH':
        serializer = self.get_serializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], url_path='update-password-by-email', permission_classes=[AllowAny])
    def update_password_by_email(self, request):
        email = request.data.get('email')
        new_password = request.data.get('password')

        if not email or not new_password:
            return Response(
                {'detail': 'Se requieren el correo y la nueva contraseña.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = CustomUser.objects.get(email=email)
            user.password = make_password(new_password)  # Hashea la contraseña
            user.save()
            return Response({'detail': 'Contraseña actualizada correctamente.'}, status=status.HTTP_200_OK)
        except CustomUser.DoesNotExist:
            return Response({'detail': 'No se encontró un usuario con ese correo.'}, status=status.HTTP_404_NOT_FOUND)


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

# Sección de vistas para las reservas y pagos
class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        # Si es PATCH, devuelve todas las reservas (para permitir cambiar el status)
        if self.request.method == 'PATCH':
            return Reservation.objects.all()

        user = self.request.user
        status_filter = self.request.query_params.get('status')
        barber_id_param = self.request.query_params.get('barber_id')

        if user.is_authenticated:
            if user.role == 0:  # Admin
                queryset = Reservation.objects.all()
            elif user.role == 1:  # Barbero
                queryset = Reservation.objects.filter(id_barber=user)
            elif user.role == 2:  # Cliente
                queryset = Reservation.objects.filter(id_client=user)
            else:
                queryset = Reservation.objects.none()
        else:
            if barber_id_param:
                try:
                    barber = CustomUser.objects.get(id=barber_id_param, role=1)
                    queryset = Reservation.objects.filter(id_barber=barber)
                except CustomUser.DoesNotExist:
                    queryset = Reservation.objects.none()
            else:
                queryset = Reservation.objects.none()

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset

 

# Método para manejar la creación de reservas
def perform_create(self, serializer):
    """Realiza la creación de la reserva, asignando cliente y barbero."""

    # Determinar el cliente
    if self.request.user.is_authenticated:
        client = self.request.user
    else:
        client = CustomUser.objects.get(id=8    )

    # Obtener el barbero
    barber_id = self.request.data.get('id_barber')
    if barber_id:
        try:
            barber = CustomUser.objects.get(id=barber_id, role=1)
        except CustomUser.DoesNotExist:
            return Response({"detail": "El barbero no existe."}, status=status.HTTP_400_BAD_REQUEST)
    else:
        return Response({"detail": "Se requiere el id del barbero."}, status=status.HTTP_400_BAD_REQUEST)

    # Guardar la reserva
    reserva = serializer.save(id_client=client, id_barber=barber)

    # ✅ Retornar los datos de la reserva al frontend
    return Response(self.get_serializer(reserva).data, status=status.HTTP_201_CREATED)


def partial_update(self, request, *args, **kwargs):
            """
            Override partial_update para permitir solo cambiar el campo 'status' y nada más.
            """
            # Limitar los campos que pueden actualizarse por PATCH
            allowed_fields = {'status'}

            # Comprobar si hay campos no permitidos en la petición
            data = request.data
            if any(field not in allowed_fields for field in data.keys()):
                return Response(
                    {"detail": "Solo se permite actualizar el campo 'status'."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Llamamos a la implementación base que hace el update
            return super().partial_update(request, *args, **kwargs)

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



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    user = request.user
    return Response({
        'id': user.id,
        'email': user.email,
        'role': user.role,
        'first_name': user.first_name,
        'is_active': user.is_active,
        'phone_number': user.phone_number,
    })



@api_view(['POST'])
def register_social_user(request):
    email = request.data.get('email')
    name = request.data.get('name')
    role = 2  # Usuario normal

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
        # Si ya existe, actualiza password y activa el usuario
        user.password = password
        user.is_active = True
        user.save()
        return Response({'message': 'Usuario ya existe, password actualizado'}, status=status.HTTP_200_OK)

    return Response({'message': 'Usuario creado correctamente'}, status=status.HTTP_201_CREATED)
    
@api_view(['GET'])
def horas_ocupadas(request):
    date_str = request.GET.get('date')
    barber_id = request.GET.get('id_barber')

    if not date_str or not barber_id:
        return Response({'error': 'Parámetros requeridos: date, id_barber'}, status=400)

    try:
        date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return Response({'error': 'Formato de fecha inválido, usa YYYY-MM-DD'}, status=400)

    reservations = Reservation.objects.filter(date__date=date, id_barber=barber_id)
    horas = [res.date.strftime("%H:%M") for res in reservations]

    return Response(horas)  