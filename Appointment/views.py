from django.http import Http404
from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime, date, timedelta
from django.db.models import Q

from .models import DoctorSchedule, Appointment, DoctorDayOff
from Account.models import CustomUser
from .serializers import (
    DoctorSerializer, DoctorScheduleSerializer, AppointmentSerializer,
    DoctorDayOffSerializer, DoctorAvailabilitySerializer, BookAppointmentSerializer
)


class AvailableDoctorsView(generics.ListAPIView):
    """
    Get all available doctors with their specializations
    """
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        specialization = self.request.query_params.get('specialization', None)
        queryset = CustomUser.objects.filter(user_type='doctor')
        
        if specialization:
            queryset = queryset.filter(specialization__icontains=specialization)
        
        return queryset


class DoctorScheduleView(generics.ListAPIView):
    """
    Get doctor's weekly schedule
    """
    serializer_class = DoctorScheduleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        doctor_id = self.kwargs.get('doctor_id')
        return DoctorSchedule.objects.filter(doctor_id=doctor_id)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def doctor_availability(request, doctor_id):
    """
    Get doctor's availability for a specific date range
    """
    serializer = DoctorAvailabilitySerializer(data=request.query_params)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    start_date = data['start_date']
    end_date = data.get('end_date', start_date)
    
    doctor = get_object_or_404(CustomUser, id=doctor_id, user_type='doctor')
    
    availability = []
    current_date = start_date
    
    while current_date <= end_date:
        day_of_week = current_date.weekday()
        
        # Get doctor's schedule for this day
        schedule = DoctorSchedule.get_schedule_for_date(doctor, current_date)
        
        # Check if doctor has a day off
        day_off = DoctorDayOff.objects.filter(
            doctor=doctor,
            date=current_date
        ).first()
        
        day_data = {
            'date': current_date.isoformat(),
            'day_name': current_date.strftime('%A'),
            'is_available': False,
            'slots': [],
            'reason_unavailable': None
        }
        
        if day_off:
            day_data['reason_unavailable'] = day_off.reason or 'Day off'
        elif schedule and schedule.is_working_day:
            day_data['is_available'] = True
            day_data['slots'] = schedule.get_available_slots(current_date)
            day_data['working_hours'] = {
                'start': schedule.start_time.strftime('%H:%M'),
                'end': schedule.end_time.strftime('%H:%M')
            }
        else:
            day_data['reason_unavailable'] = 'Not a working day'
        
        availability.append(day_data)
        current_date += timedelta(days=1)
    
    return Response({
        'doctor': DoctorSerializer(doctor).data,
        'availability': availability
    })


# class BookAppointmentView(generics.CreateAPIView):
#     serializer_class = BookAppointmentSerializer
#     permission_classes = [IsAuthenticated]

#     def create(self, request, *args, **kwargs):
#         try:
#             # Debug incoming request
#             print(f"Incoming request data: {request.data}")
#             print(f"Current time: {timezone.now()}")
            
#             response = super().create(request, *args, **kwargs)
#             print("Appointment created successfully")
#             return response
            
#         except Exception as e:
#             print(f"Error in BookAppointmentView: {str(e)}")
#             return Response(
#                 {"error": str(e)},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
class BookAppointmentView(generics.CreateAPIView):
    serializer_class = BookAppointmentSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            print(f"Incoming request data: {request.data}")
            print(f"Current time: {timezone.now()}")

            doctor_id = request.data.get('doctor')
            appointment_date = request.data.get('appointment_date')
            if not doctor_id or not appointment_date:
                return Response({"error": "Doctor and appointment_date are required."}, status=400)

            doctor = get_object_or_404(CustomUser, id=doctor_id, user_type='doctor')
            date_obj = datetime.strptime(appointment_date, "%Y-%m-%d").date()

            # Use the robust schedule lookup
            schedule = DoctorSchedule.get_schedule_for_date(doctor, date_obj)
            if not schedule or not schedule.is_working_day:
                return Response({"error": "No working schedule for this doctor on this date."}, status=400)

            # Optionally: check if the requested time is within the schedule's available slots

            response = super().create(request, *args, **kwargs)
            print("Appointment created successfully")
            return response

        except Exception as e:
            print(f"Error in BookAppointmentView: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class PatientAppointmentsView(generics.ListAPIView):
    """
    Get all appointments for the current patient
    """
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type != 'patient':
            return Appointment.objects.none()
        
        status_filter = self.request.query_params.get('status', None)
        queryset = Appointment.objects.filter(patient=user)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-appointment_date', '-appointment_time')


class DoctorAppointmentsView(generics.ListAPIView):
    """
    Get all appointments for the current doctor
    """
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type != 'doctor':
            return Appointment.objects.none()
        
        status_filter = self.request.query_params.get('status', None)
        date_filter = self.request.query_params.get('date', None)
        
        queryset = Appointment.objects.filter(doctor=user)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        if date_filter:
            try:
                filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                queryset = queryset.filter(appointment_date=filter_date)
            except ValueError:
                pass
        
        return queryset.order_by('appointment_date', 'appointment_time')


class AppointmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Get, update, or cancel a specific appointment
    """
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'patient':
            return Appointment.objects.filter(patient=user)
        elif user.user_type == 'doctor':
            return Appointment.objects.filter(doctor=user)
        return Appointment.objects.none()
    
    # def update(self, request, *args, **kwargs):
    #     appointment = self.get_object()
        
    #     # Only allow status updates for doctors, and notes updates
    #     if request.user.user_type == 'doctor':
    #         allowed_fields = ['status', 'doctor_notes']
    #     else:
    #         allowed_fields = ['notes']
        
    #     # Filter request data to only include allowed fields
    #     filtered_data = {k: v for k, v in request.data.items() if k in allowed_fields}
        
    #     serializer = self.get_serializer(appointment, data=filtered_data, partial=True)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_update(serializer)
        
    #     return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        try:
            instance = self.get_object()
        except Http404:
            return Response({"detail": "Appointment not found or access denied."}, status=404)

        # Restrict update fields based on user type
        if request.user.user_type == 'doctor':
            allowed_fields = ['status', 'doctor_notes']
        else:
            allowed_fields = ['notes']

        filtered_data = {k: v for k, v in request.data.items() if k in allowed_fields}

        serializer = self.get_serializer(instance, data=filtered_data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=400)


    def destroy(self, request, *args, **kwargs):
            """
            Cancel an appointment (soft delete by changing status)
            """
            appointment = self.get_object()
            
            if not appointment.can_be_cancelled():
                return Response(
                    {'error': 'Appointment cannot be cancelled. It\'s either too close to the appointment time or already completed/cancelled.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            appointment.status = 'cancelled'
            appointment.save()
            
            return Response({'message': 'Appointment cancelled successfully'})


# # Views for doctors to manage their schedule (optional)
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import DoctorSchedule
from .serializers import DoctorScheduleSerializer
from django.db.models import Q
from datetime import date, timedelta

class DoctorScheduleManageView(generics.ListCreateAPIView, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DoctorScheduleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Get both recurring and current week's schedules for the logged-in doctor
        today = date.today()
        current_week = today - timedelta(days=today.weekday())
        return DoctorSchedule.objects.filter(
            Q(doctor=self.request.user) &
            (Q(is_recurring=True) | Q(week_start_date=current_week))
        ).order_by('week_start_date', 'day_of_week')
    
    def get_object(self):
        # Custom object lookup to ensure we only get the doctor's own schedules
        queryset = self.filter_queryset(self.get_queryset())
        filter_kwargs = {'pk': self.kwargs['pk']}
        obj = get_object_or_404(queryset, **filter_kwargs)
        self.check_object_permissions(self.request, obj)
        return obj
    
    def perform_create(self, serializer):
        serializer.save(doctor=self.request.user)
# class DoctorScheduleManageView(generics.ListCreateAPIView):
#     serializer_class = DoctorScheduleSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         return DoctorSchedule.objects.filter(doctor=self.request.user)

#     def perform_create(self, serializer):
#         # Directly assign the current user as the doctor
#         serializer.save(doctor=self.request.user)



class DoctorDayOffView(generics.ListCreateAPIView):
    """
    Manage doctor's days off (for doctors only)
    """
    serializer_class = DoctorDayOffSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type != 'doctor':
            return DoctorDayOff.objects.none()
        return DoctorDayOff.objects.filter(doctor=user)
    
    def perform_create(self, serializer):
        serializer.save(doctor=self.request.user)
