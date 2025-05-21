from rest_framework.permissions import BasePermission
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

class IsAdmin(BasePermission):
    """
    Permite acceso solo a los administradores.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 0  # 0 = Admin
    
class CanEditOwnProfile(BasePermission):
    """
    Permite a los usuarios editar sus propios datos, excepto los campos restringidos.
    Solo los administradores pueden editar `is_active`, `role` y `salary`.
    """

    def has_object_permission(self, request, view, obj):
        # Solo los admins pueden editar `is_active`, `role` y `salary`
        if request.user.role == 0:  # 0 = Admin
            return True

        # Si no es admin, solo puede editar su propio perfil
        return obj == request.user

class IsBarberOrAdmin(BasePermission):
    """
    Permite acceso solo a administradores y barberos para modificar servicios.
    Los clientes solo pueden ver los servicios.
    """
    def has_permission(self, request, view):
        # Permitir acceso de lectura a todos (GET, HEAD, OPTIONS)
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        # Solo permitir POST, PUT, DELETE a admin (0) y barberos (1)
        return request.user.is_authenticated and request.user.role in [0, 1]

class UserPermissionsHelper:
    """Clase para manejar permisos y validaciones en UserViewSet."""

    @staticmethod
    def get_permissions(view):
        """Define permisos según la acción en UserViewSet."""
        if view.action == 'create':
            return [AllowAny()]
        elif view.action == 'destroy':
            return [IsAdmin()]
        elif view.action in ['update', 'partial_update']:
            return [CanEditOwnProfile()]
        return [AllowAny()]

    @staticmethod
    def perform_create(serializer, request):
        """Valida que los barberos tengan salario al crearse."""
        role = request.data.get('role', 2)  # Cliente por defecto (2)
        salary = request.data.get('salary')

        if int(role) == 1 and not salary:  # Si el rol es barbero y no se proporciona salario
            return Response(
                {"detail": "El salario es obligatorio para los barberos."},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer.save(role=role, is_active=True)

    @staticmethod
    def perform_update(serializer, request, user):
        """Restringe la edición de ciertos campos solo a admin."""
        if request.user.role != 0:  # No es Admin
            restricted_fields = ['is_active', 'role', 'salary']
            for field in restricted_fields:
                serializer.validated_data.pop(field, None)  # Eliminar si está presente
        serializer.save()

    @staticmethod
    def get_filtered_queryset(view, queryset):
        """Filtra los usuarios por rol si se proporciona en la URL."""
        role = view.request.query_params.get('role')
        if role is not None:
            return queryset.filter(role=role)
        return queryset










