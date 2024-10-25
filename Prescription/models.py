from django.db import models
from Account.models import CustomUser

class Prescription(models.Model):
    patient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="prescriptions")
    doctor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="doctor_prescriptions")
    medicine_name = models.CharField(max_length=255)
    dosage = models.CharField(max_length=255)
    instructions = models.TextField()
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Prescription for {self.patient.full_name} by {self.doctor.full_name}"
