from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, BarberSchedule, Service, Reservation, Payment, UserCard

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Información personal', {'fields': ('first_name', 'last_name', 'phone_number')}),
        ('Rol y permisos', {'fields': ('role', 'is_staff', 'is_superuser', 'is_active')}),
        ('Otros datos', {'fields': ('reward_points', 'salary')}),
    )

    list_display = ('email', 'first_name', 'last_name', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)  # Cambiamos username por email
    
@admin.register(BarberSchedule)
class BarberScheduleAdmin(admin.ModelAdmin):
    list_display = ('get_barber_id', 'days', 'start_time', 'end_time')  # Campos visibles en la lista
    list_filter = ('days',)  # Filtro en el panel de admin
    search_fields = ('id_barber__username',)  # Permite buscar por el nombre del barbero
    ordering = ('id_barber',)  # Ordenar por barbero
    
    # Método para obtener el ID del barbero
    def get_barber_id(self, obj):
        return obj.id_barber.id  # Devuelve el ID del barbero
    get_barber_id.admin_order_field = 'id_barber'  # Permite ordenar por este campo
    get_barber_id.short_description = 'Barber ID'  # Nombre en la columna del admin
    
@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_client_email', 'person_name', 'get_barber_name', 'id_service', 'date', 'status', 'pay')  # Mostrar nombre del barbero y el correo del cliente
    list_filter = ('status', 'pay', 'id_barber', 'id_client')  # Filtros
    search_fields = ('id_client__email', 'id_barber__email', 'id_service__name')  # Permite buscar por email o nombre de servicio
    ordering = ('date',)

    # Método para obtener el correo del cliente
    def get_client_email(self, obj):
        return f"{obj.id_client.email}"  # Devuelve el nombre completo del cliente
    get_client_email.admin_order_field = 'id_client'  # Permite ordenar por este campo
    get_client_email.short_description = 'Client Email'  # Nombre en la columna del admin

    # Método para obtener el nombre completo del barbero
    def get_barber_name(self, obj):
        return f"{obj.id_barber.first_name}"  # Devuelve el nombre completo del barbero
    get_barber_name.admin_order_field = 'id_barber'  # Permite ordenar por este campo
    get_barber_name.short_description = 'Barber Name'  # Nombre en la columna del admin



# Registrar Servicios en el Admin
# Registrar Servicios en el Admin
@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'category', 'name', 'description', 'time', 'price', 'active_service')  # Campos visibles
    list_filter = ('active_service', 'category')  # Filtro para ver solo servicios activos
    search_fields = ('category', 'name', 'description')  # Permite buscar por nombre y descripción del servicio
    ordering = ('id',)
    
    
# Registrar Pagos en el Admin
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('reservation', 'amount', 'method', 'created_at', 'updated_at')  # Campos visibles
    list_filter = ('method', 'created_at')  # Filtros
    search_fields = ('reservation__id', 'amount', 'method')  # Permite buscar por reserva y método de pago
    ordering = ('created_at',)
