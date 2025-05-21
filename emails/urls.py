# emails/urls.py
from django.urls import path
from .views import AppointmentCancellationEmailView, AppointmentConfirmationEmailView, PasswordRecoveryCodeView, ValidateRecoveryCodeView

urlpatterns = [
    path('appointment-cancellation/', AppointmentCancellationEmailView.as_view(), name='appointment-cancellation'),
    path('appointment-confirmation/', AppointmentConfirmationEmailView.as_view(), name='appointment-confirmation'),
    path('recovery-code/', PasswordRecoveryCodeView.as_view(), name='password-recovery-code'),
    path('validate-recovery-code/', ValidateRecoveryCodeView.as_view(), name='validate-recovery-code'),
]
