from django.contrib.auth import get_user_model
from .models import Service

User = get_user_model()

class BarberFlyweight:
    _cache = {}
    
    @classmethod
    def get_barber(cls, barber_id):
        # Verifica si el barber_id ya está en la caché        
        if barber_id not in cls._cache:
            try:
                # Si no está en la caché, obtiene el objeto User correspondiente                
                barber = User.objects.get(id=barber_id)
                # Almacena los datos relevantes del barbero en la caché                
                cls._cache[barber_id] = {
                    'name': barber.username,
                    'specialties': list(barber.services_offered.all().values_list('name', flat=True))
                }
            except User.DoesNotExist:
                # Si el barbero no existe, retorna None                
                return None
        return cls._cache[barber_id]
    
class ServiceFlyweight:
    _cache = {}
    
    @classmethod
    def get_service(cls, service_id):
        # Verifica si el service_id ya está en la caché        
        if service_id not in cls._cache:
            try:
                # Si no está en la caché, obtiene el objeto Service correspondiente                
                service = Service.objects.get(id=service_id)
                # Almacena los datos relevantes del servicio en la caché                
                cls._cache[service_id] = {
                    'name': service.name,
                    'price': float(service.price),
                    'duration': service.time
                }
            except Service.DoesNotExist:
                return None
        return cls._cache[service_id]
    
class PaymentFlyweight:
    _cache = {}
    
    @classmethod
    def get_payment_data(cls, payment_id):
        """Cachea datos de pagos recurrentes"""
        if payment_id not in cls._cache:
            from .models import Payment
            payment = Payment.objects.get(id=payment_id)
            cls._cache[payment_id] = {
                'amount': float(payment.amount),
                'service': payment.reservation.id_service.name,
                'date': payment.created_at
            }
        return cls._cache[payment_id]