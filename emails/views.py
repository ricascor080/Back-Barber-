# emails/views.py
import random
from django.conf import settings
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from accounts.models import Reservation, CustomUser

# Email para la cancelación de citas
class AppointmentCancellationEmailView(APIView):
    def post(self, request, *args, **kwargs):
        reservation_id = request.data.get("reservation_id")
        
        # Obtener la reservación por ID
        try:
            reservation = Reservation.objects.get(id=reservation_id)
            barber = reservation.id_barber
            customer = reservation.id_client  # Cliente relacionado con la reserva
            appointment_time = reservation.date            
        except Reservation.DoesNotExist:
            return Response({"error": "Reservación no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        # Obtener el correo del cliente
        customer_email = customer.email

        # Crear el contenido del correo de cancelación
        subject = 'Tu cita en BARBER SHOP ha sido cancelada'
        message = f"""
            <html>
            <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; color: #333;">
                <div style="width: 80%; margin: auto; padding: 20px; background-color: white; border-radius: 10px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);">
                    <h2 style="color: #2c3e50;">Cancelacion de tu cita</h2>
                    <p>Hola {customer.first_name} {customer.last_name},</p>
                    <p>Tu cita en BARBER SHOP ha sido cancelada:</p>
                    <p><strong>Barbero:</strong> {barber.first_name} {barber.last_name}</p>
                    <p><strong>Hora de la cita:</strong> {appointment_time}</p>
                    <p>Favor de contactarse con BARBER SHOP</p>
                    <p>Saludos,<br>El equipo de BARBER SHOP</p>
                    <footer style="margin-top: 20px; font-size: 12px; color: #bdc3c7; text-align: center;">
                        <p>Este es un correo automático. No respondas a este mensaje.</p>
                    </footer>
                </div>
            </body>
        </html>
        """

        # Enviar el correo con el remitente personalizado
        email = EmailMessage(
            subject,
            message,
            'BARBER SHOP <noreply@barbershop.com>',  # Nombre del remitente personalizado
            [customer_email],  # Enviar al correo del cliente
        )
        email.content_subtype = "html"  # Para que el mensaje sea interpretado como HTML
        email.send(fail_silently=False)

        return Response({"message": "Correo de cancelación enviado."}, status=status.HTTP_200_OK)

# Email para la confirmación de citas
class AppointmentConfirmationEmailView(APIView):
    def post(self, request, *args, **kwargs):
        reservation_id = request.data.get("reservation_id")
        
        # Obtener la reservación por ID
        try:
            reservation = Reservation.objects.get(id=reservation_id)
            barber = reservation.id_barber
            customer = reservation.id_client  # Cliente relacionado con la reserva
            appointment_time = reservation.date
        except Reservation.DoesNotExist:
            return Response({"error": "Reservación no encontrada."}, status=status.HTTP_404_NOT_FOUND)

        # Obtener el correo del cliente
        customer_email = customer.email

        # Crear el contenido del correo de confirmación
        subject = 'Confirmación de tu cita en BARBER SHOP'
        message = f"""
        <html>
            <body>
                <p>Hola {customer.first_name} {customer.last_name},</p>
                <p>Tu cita en BARBER SHOP ha sido confirmada.</p>
                <p><strong>Barbero:</strong> {barber.first_name} {barber.last_name}</p>
                <p><strong>Hora de la cita:</strong> {appointment_time}</p>
                <p>¡Te esperamos!</p>
                <p>Saludos,<br>El equipo de BARBER SHOP</p>
            </body>
        </html>
        """

        # Enviar el correo con el remitente personalizado
        email = EmailMessage(
            subject,
            message,
            'BARBER SHOP <noreply@barbershop.com>',  # Nombre del remitente personalizado
            [customer_email],  # Enviar al correo del cliente
        )
        email.content_subtype = "html"  # Para que el mensaje sea interpretado como HTML
        email.send(fail_silently=False)

        return Response({"message": "Correo de confirmación enviado."}, status=status.HTTP_200_OK)

# Email para la recuperación de contraseña
class PasswordRecoveryCodeView(APIView):
    def post(self, request):
        email = request.data.get("email")
        
        # Validar si el usuario existe
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            return Response({"detail": "Email no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        # Generar el código aleatorio de 5 dígitos
        recovery_code = random.randint(10000, 99999)
        
        # Guardar el código de recuperación en el usuario
        user.password_recovery_code = recovery_code
        user.save()

        # Crear el contenido del correo con formato HTML
        subject = "Recuperación de Contraseña - BARBER SHOP"
        message = f"""
        <html>
            <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; color: #333;">
                <div style="width: 80%; margin: auto; padding: 20px; background-color: white; border-radius: 10px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);">
                    <h2 style="color: #2c3e50;">Recuperación de Contraseña</h2>
                    <p>Hola {user.first_name},</p>
                    <p>Hemos recibido una solicitud para recuperar tu contraseña. Tu código de recuperación es el siguiente:</p>
                    <div style="background-color: #ecf0f1; padding: 10px; font-size: 18px; font-weight: bold; color: #e74c3c; text-align: center;">
                        {recovery_code}
                    </div>
                    <p>Si no solicitaste este código, por favor ignora este correo.</p>
                    <p>Saludos,<br>El equipo de BARBER SHOP</p>
                    <footer style="margin-top: 20px; font-size: 12px; color: #bdc3c7; text-align: center;">
                        <p>Este es un correo automático. No respondas a este mensaje.</p>
                    </footer>
                </div>
            </body>
        </html>
        """

        # Enviar el correo con el código de recuperación
        email = EmailMessage(
            subject,
            message,
            'BARBER SHOP <noreply@barbershop.com>',
            [email],
        )
        email.content_subtype = "html"  # Para que el mensaje sea interpretado como HTML
        email.send(fail_silently=False)

        return Response({"detail": "Código enviado a tu correo."}, status=status.HTTP_200_OK)


# Email para validar el código de recuperación de contraseña  
class ValidateRecoveryCodeView(APIView):
        def post(self, request):
            email = request.data.get("email")
            code = request.data.get("code")
            
            # Validar si el usuario existe
            try:
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                return Response({"detail": "Email no encontrado."}, status=status.HTTP_404_NOT_FOUND)

            # Validar si el código de recuperación es correcto
            if user.password_recovery_code == int(code):
                return Response({"detail": "Código correcto."}, status=status.HTTP_200_OK)
            else:
                return Response({"detail": "Código incorrecto."}, status=status.HTTP_400_BAD_REQUEST)
