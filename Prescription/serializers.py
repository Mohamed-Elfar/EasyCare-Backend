from rest_framework import serializers
from .models import Prescription
class PrescriptionSerializer(serializers.ModelSerializer):
    doctor = serializers.CharField(source='doctor.full_name', read_only=True)  # Display doctor's full name
    patient = serializers.CharField(source='patient.full_name', read_only=True)  # Display patient's full name

    class Meta:
        model = Prescription
        fields = ['medicine_name', 'dosage', 'instructions', 'created_at', 'doctor', 'patient']
        read_only_fields = ['doctor', 'patient', 'created_at']

