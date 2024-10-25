from django.urls import path
from .views import AddPrescriptionView

urlpatterns = [
    path('patients/<str:patient_national_id>/prescriptions/', AddPrescriptionView.as_view(), name='add_prescription'),
]
