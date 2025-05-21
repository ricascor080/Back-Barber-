from .models import Reservation, Service, Payment, UserCard
from django.contrib.auth import get_user_model
from datetime import datetime

class ReservationFactory:
    @staticmethod
    def create_reservation(validated_data):
        """Crea una reserva ignorando autenticación"""
        # Copia los datos validados para evitar modificar el original        
        reservation_data = validated_data.copy()
        # Crea y retorna una instancia de Reservation con los datos proporcionados
        return Reservation.objects.create(**reservation_data)

class ServiceFactory:
    @staticmethod
    def create_service(validated_data):
        """Crea servicios con activación automática"""
        # Copia los datos validados para evitar modificar el original        
        service_data = validated_data.copy()
        # Establece el servicio como activo por defecto        
        service_data['active_service'] = True  # Activo por defecto
        # Crea y retorna una instancia de Service con los datos proporcionados        
        return Service.objects.create(**service_data)

User = get_user_model()

class CardFactory:
    @staticmethod
    def create_card(validated_data):
        """Crea tarjeta"""
        user = User.objects.get(id=1)
        return UserCard.objects.create(user=user, **validated_data)

class PaymentFactory:
    @staticmethod
    def create_payment(validated_data, service_price):
        """Crea pago con lógica de negocio integrada"""
        payment_data = validated_data.copy() # Copia los datos validados para evitar modificar el original
        payment_data['amount'] = service_price # Establece el monto del pago
        return Payment.objects.create(**payment_data)