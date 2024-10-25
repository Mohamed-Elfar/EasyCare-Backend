from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CustomUser
from .serializers import PrescriptionSerializer
from django.shortcuts import get_object_or_404

class AddPrescriptionView(APIView):
    def post(self, request, patient_national_id):
        doctor = request.user
        patient = get_object_or_404(CustomUser, national_id=patient_national_id, user_type='patient')

        if doctor.user_type != 'doctor':
            return Response({"error": "Only doctors can add prescriptions"}, status=status.HTTP_403_FORBIDDEN)

        serializer = PrescriptionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(doctor=doctor, patient=patient)
            response_data = {
                "message": "Prescription added successfully"
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
