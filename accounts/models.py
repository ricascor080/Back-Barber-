from django.db import models
from django.contrib.auth.models import AbstractUser

# Modelo del usuario personalizado
class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        (0, 'Admin'),
        (1, 'Barber'),
        (2, 'Client'),
    )
    
    email = models.EmailField(unique=True)  # Email como campo único
    
    username = models.CharField(max_length=150, blank=True, null=True)   # para crear el super usuario se comento 
    
    #Se crea un campo de rol con las opciones de ROLE_CHOICES
    role = models.PositiveSmallIntegerField(choices=ROLE_CHOICES, default=0)
    
    #Se crea un campo de activo
    is_active = models.BooleanField(default=True)

    #Puntos de recompensa
    reward_points = models.PositiveIntegerField(default=0)
    
    #Número de teléfono
    phone_number = models.CharField(max_length=10, default="0000000000", blank=False, null=False)

    #Salario (solo aplicable a Barbers, pero por simplicidad ponemos null)
    salary = models.DecimalField(max_digits=10, decimal_places=2, default=None, blank=True, null=True)
    
    # Nuevo campo para el código de recuperación de contraseña
    password_recovery_code = models.PositiveIntegerField(null=True, blank=True)
    
    USERNAME_FIELD = 'email'  # Ahora el usuario se autentica con email # Se comento el username para lo del super usuario
    REQUIRED_FIELDS = []  # Si quieres agregar más campos requeridos para superusuarios, agréguelos aquí

    class Meta:
        db_table = 'users' #La tabla en la BD se llame users

    def __str__(self):
        #Muestra el nombre de usuario y el rol
        return f"{self.username} ({self.get_role_display()})"
    
    def save(self, *args, **kwargs):
        if self.role == 0:  # Si el rol es Admin
            self.is_staff = True  # Activamos is_staff automáticamente
        else:
            self.is_staff = False  # Desactivamos is_staff si no es Admin

        super().save(*args, **kwargs)  # Llamamos al método save original

# Modelo de los horarios de los barberos
class BarberSchedule(models.Model):
    id_schedule = models.AutoField(primary_key=True)
    id_barber = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        limit_choices_to={'role': 1},  # Solo usuarios con rol de "Barber"
        related_name='schedules'
    )
    days = models.JSONField(default=list)  # Almacenar días como JSON (lista)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        db_table = 'barber_schedule'

    def __str__(self):
        return f"Horario de {self.id_barber.username}: {self.days}"

# Modelo de los servicios   
class Service(models.Model):
    SERVICES_CHOICES = (
        (1, 'Cortes y Estilos'),
        (2, 'Barba y Afeitado'),
        (3, 'Tratamientos y Cuidado'),
    )
    
    category = models.PositiveSmallIntegerField(choices=SERVICES_CHOICES, default=1, blank=False, null=False)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    time = models.IntegerField(default=30)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    active_service = models.BooleanField(default=True)

    def _str_(self):
        return self.name

# Modelo de las reservas
class Reservation(models.Model):
    # Se define el estado de la reserva con las opciones disponibles
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('confirmed', 'Confirmada'),
        ('canceled', 'Cancelada'),
        ('completed', 'Completada')
    ]
    
    id_client = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='client_reservations')
    id_barber = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='barber_reservations')
    id_service = models.ForeignKey(Service, on_delete=models.CASCADE)
    date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    pay = models.BooleanField(default=False)
    person_name = models.CharField(max_length=100, null=True, blank=True) # Nombre de la persona que hace la reserva

# Modelo de los pagos
class Payment(models.Model):
    METHOD_CHOICES = [('cash', 'Efectivo Debito'), ('card', 'Tarjeta Credito')]

    reservation = models.OneToOneField(Reservation, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2, blank=True)
    method = models.CharField(max_length=15, choices=METHOD_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.amount:  # Si no se ha proporcionado amount, obtenemos el precio del servicio
            self.amount = self.reservation.service.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Payment {self.id} - {self.reservation}"

# Modelo de las tarjetas de usuario    
class UserCard(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    card_number = models.CharField(max_length=16)
    expiration_month = models.CharField(max_length=2)
    expiration_year = models.CharField(max_length=4)

    nickname = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nickname} - ****{self.card_number[-4:]}"
