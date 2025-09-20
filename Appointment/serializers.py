from rest_framework import serializers
from django.utils import timezone
from datetime import datetime, date, timedelta
from .models import DoctorSchedule, Appointment, DoctorDayOff
from Account.models import CustomUser
from rest_framework.exceptions import PermissionDenied
from rest_framework import serializers
from django.utils import timezone
from django.utils.timezone import make_aware, is_naive
from datetime import datetime
from .models import Appointment, DoctorSchedule, DoctorDayOff
from rest_framework.exceptions import PermissionDenied
from rest_framework import serializers
from .models import DoctorSchedule
from datetime import date, timedelta

class DoctorSerializer(serializers.ModelSerializer):
    """
    Serializer for doctor information in appointment context
    """
    class Meta:
        model = CustomUser
        fields = ['id', 'full_name', 'email', 'phone_number', 'hospital', 'clinic', 'specialization']

class DoctorScheduleSerializer(serializers.ModelSerializer):
    day_name = serializers.SerializerMethodField()
    doctor_name = serializers.CharField(source='doctor.full_name', read_only=True)
    week_range = serializers.SerializerMethodField()
    
    class Meta:
        model = DoctorSchedule
        fields = [
            'id', 'doctor', 'doctor_name',
            'day_of_week', 'day_name', 
            'start_time', 'end_time',
            'is_working_day', 'appointment_duration',
            'week_start_date', 'is_recurring', 'week_range'
        ]
        read_only_fields = ['doctor']
    
    def get_day_name(self, obj):
        return dict(DoctorSchedule.WEEKDAYS).get(obj.day_of_week, '')
    
    def get_week_range(self, obj):
        end_date = obj.week_start_date + timedelta(days=6)
        return f"{obj.week_start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"
    
    def validate(self, data):
        if data.get('is_recurring', False):
            # For recurring schedules, set week_start_date to a fixed value
            data['week_start_date'] = date(2000, 1, 1)  # Arbitrary old date
        elif 'week_start_date' not in data:
            # For non-recurring, default to current week
            today = date.today()
            data['week_start_date'] = today - timedelta(days=today.weekday())
        
        if data['start_time'] >= data['end_time']:
            raise serializers.ValidationError("End time must be after start time")
        
        return data
# class AppointmentSerializer(serializers.ModelSerializer):
#     """
#     Serializer for appointments
#     """
#     patient_name = serializers.CharField(source='patient.full_name', read_only=True)
#     doctor_name = serializers.CharField(source='doctor.full_name', read_only=True)
#     doctor_specialization = serializers.CharField(source='doctor.specialization', read_only=True)
#     can_cancel = serializers.SerializerMethodField()
#     appointment_datetime = serializers.SerializerMethodField()
    
#     class Meta:
#         model = Appointment
#         fields = ['id', 'patient', 'patient_name', 'doctor', 'doctor_name', 
#                  'doctor_specialization', 'appointment_date', 'appointment_time', 
#                  'appointment_datetime', 'status', 'notes', 'doctor_notes', 
#                  'can_cancel', 'created_at', 'updated_at']
#         read_only_fields = ['doctor_notes', 'created_at', 'updated_at']
    
#     def get_can_cancel(self, obj):
#         return obj.can_be_cancelled()
    
#     def get_appointment_datetime(self, obj):
#         return obj.appointment_datetime.isoformat() if obj.appointment_datetime else None
    
#     # def validate(self, data):
#     #     """
#     #     Validate appointment data
#     #     """
#     #     appointment_date = data.get('appointment_date')
#     #     appointment_time = data.get('appointment_time')
#     #     doctor = data.get('doctor')
        
#     #     # Check if appointment is in the future
#     #     appointment_datetime = datetime.combine(appointment_date, appointment_time)
#     #     if appointment_datetime <= timezone.now():
#     #         raise serializers.ValidationError("Appointment must be scheduled for a future date and time.")
        
#     #     # Check if doctor has a schedule for this day
#     #     day_of_week = appointment_date.weekday()
#     #     schedule = DoctorSchedule.objects.filter(
#     #         doctor=doctor,
#     #         day_of_week=day_of_week,
#     #         is_working_day=True
#     #     ).first()
        
#     #     if not schedule:
#     #         raise serializers.ValidationError("Doctor is not available on this day.")
        
#     #     # Check if time is within doctor's working hours
#     #     if not (schedule.start_time <= appointment_time <= schedule.end_time):
#     #         raise serializers.ValidationError(
#     #             f"Appointment time must be between {schedule.start_time} and {schedule.end_time}."
#     #         )
        
#     #     # Check if doctor has a day off on this date
#     #     if DoctorDayOff.objects.filter(doctor=doctor, date=appointment_date).exists():
#     #         raise serializers.ValidationError("Doctor is not available on this date.")
        
#     #     # Check if slot is already booked (for create operations)
#     #     if not self.instance:  # Only check for new appointments
#     #         existing_appointment = Appointment.objects.filter(
#     #             doctor=doctor,
#     #             appointment_date=appointment_date,
#     #             appointment_time=appointment_time,
#     #             status__in=['confirmed', 'pending']
#     #         ).exists()
            
#     #         if existing_appointment:
#     #             raise serializers.ValidationError("This time slot is already booked.")
        
#     #     return data
#     def validate(self, data):
#         """
#         Validate appointment data
#         """
#         # Skip full validation if required fields are missing (e.g., partial update)
#         appointment_date = data.get('appointment_date') or (self.instance and self.instance.appointment_date)
#         appointment_time = data.get('appointment_time') or (self.instance and self.instance.appointment_time)
#         doctor = data.get('doctor') or (self.instance and self.instance.doctor)

#         if not (appointment_date and appointment_time and doctor):
#             return data  # Skip validation for PATCH updates that don't include scheduling fields

#         # Check if appointment is in the future
#         appointment_datetime = datetime.combine(appointment_date, appointment_time)
#         if appointment_datetime <= timezone.now():
#             raise serializers.ValidationError("Appointment must be scheduled for a future date and time.")

#         # Check if doctor has a schedule for this day
#         day_of_week = appointment_date.weekday()
#         schedule = DoctorSchedule.objects.filter(
#             doctor=doctor,
#             day_of_week=day_of_week,
#             is_working_day=True
#         ).first()

#         if not schedule:
#             raise serializers.ValidationError("Doctor is not available on this day.")

#         # Check if time is within doctor's working hours
#         if not (schedule.start_time <= appointment_time <= schedule.end_time):
#             raise serializers.ValidationError(
#                 f"Appointment time must be between {schedule.start_time} and {schedule.end_time}."
#             )

#         # Check if doctor has a day off on this date
#         if DoctorDayOff.objects.filter(doctor=doctor, date=appointment_date).exists():
#             raise serializers.ValidationError("Doctor is not available on this date.")

#         # Check if slot is already booked (for create operations)
#         if not self.instance:  # Only check for new appointments
#             existing_appointment = Appointment.objects.filter(
#                 doctor=doctor,
#                 appointment_date=appointment_date,
#                 appointment_time=appointment_time,
#                 status__in=['confirmed', 'pending']
#             ).exists()

#             if existing_appointment:
#                 raise serializers.ValidationError("This time slot is already booked.")

#         return data

from rest_framework import serializers
from datetime import datetime
from django.utils import timezone
from .models import Appointment, DoctorSchedule, DoctorDayOff

class AppointmentSerializer(serializers.ModelSerializer):
    """
    Serializer for appointments
    """
    patient_name = serializers.CharField(source='patient.full_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.full_name', read_only=True)
    doctor_specialization = serializers.CharField(source='doctor.specialization', read_only=True)
    can_cancel = serializers.SerializerMethodField()
    appointment_datetime = serializers.SerializerMethodField()
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'patient', 'patient_name', 'doctor', 'doctor_name',
            'doctor_specialization', 'appointment_date', 'appointment_time',
            'appointment_datetime', 'status', 'notes', 'doctor_notes',
            'can_cancel', 'created_at', 'updated_at'
        ]
        read_only_fields = [ 'created_at', 'updated_at']

    def get_can_cancel(self, obj):
        return obj.can_be_cancelled()
    
    def get_appointment_datetime(self, obj):
        return obj.appointment_datetime.isoformat() if obj.appointment_datetime else None

    def validate(self, data):
        appointment_date = data.get('appointment_date') or getattr(self.instance, 'appointment_date', None)
        appointment_time = data.get('appointment_time') or getattr(self.instance, 'appointment_time', None)
        doctor = data.get('doctor') or getattr(self.instance, 'doctor', None)

        # Only run validation if all three values are present (usually on creation or full update)
        if appointment_date and appointment_time and doctor:
            # ... (your existing validation logic)
            pass

        return data
class DoctorDayOffSerializer(serializers.ModelSerializer):
    """
    Serializer for doctor's days off
    """
    doctor_name = serializers.CharField(source='doctor.full_name', read_only=True)
    
    class Meta:
        model = DoctorDayOff
        fields = ['id', 'doctor', 'doctor_name', 'date', 'reason', 'created_at']
        read_only_fields = ['created_at']
class DoctorAvailabilitySerializer(serializers.Serializer):
    """
    Serializer for getting doctor availability for a specific date range
    """
    start_date = serializers.DateField()
    end_date = serializers.DateField(required=False)
    
    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date', start_date)
        
        if end_date < start_date:
            raise serializers.ValidationError("End date must be after start date.")
        
        # Limit to 30 days range
        if (end_date - start_date).days > 30:
            raise serializers.ValidationError("Date range cannot exceed 30 days.")
        
        return data

class BookAppointmentSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for booking appointments
    """
    appointment_date = serializers.DateField(input_formats=['%Y-%m-%d'])
    appointment_time = serializers.TimeField(input_formats=['%H:%M'])
    
    class Meta:
        model = Appointment
        fields = ['doctor', 'appointment_date', 'appointment_time', 'notes']
        extra_kwargs = {
            'doctor': {'required': True},
            'appointment_date': {'required': True},
            'appointment_time': {'required': True},
        }
    
    def validate(self, data):
        try:
            appointment_date = data['appointment_date']
            appointment_time = data['appointment_time']
            doctor = data['doctor']
            
            # Create timezone-aware datetime for comparison
            naive_datetime = datetime.combine(appointment_date, appointment_time)
            appointment_datetime = timezone.make_aware(naive_datetime)
            current_datetime = timezone.now()
            
            # Debug output
            print(f"Validating appointment at {appointment_datetime} (current: {current_datetime})")
            
            # Check if appointment is in the future
            if appointment_datetime <= current_datetime:
                raise serializers.ValidationError("Appointment must be scheduled for a future date and time.")
            
            # Get doctor's schedule
           # Get doctor's schedule (week-specific or recurring)
            schedule = DoctorSchedule.get_schedule_for_date(doctor, appointment_date)
            if not schedule or not schedule.is_working_day:
                raise serializers.ValidationError("Doctor is not available on this day.")
                
            # Check working hours
            if not (schedule.start_time <= appointment_time <= schedule.end_time):
                raise serializers.ValidationError(
                    f"Appointment time must be between {schedule.start_time.strftime('%H:%M')} "
                    f"and {schedule.end_time.strftime('%H:%M')}."
                )
            
            # Check day off
            if DoctorDayOff.objects.filter(doctor=doctor, date=appointment_date).exists():
                raise serializers.ValidationError("Doctor is not available on this date.")
            
            # Check slot availability
            if Appointment.objects.filter(
                doctor=doctor,
                appointment_date=appointment_date,
                appointment_time=appointment_time,
                status__in=['confirmed', 'pending']
            ).exists():
                raise serializers.ValidationError("This time slot is already booked.")
            
            return data
            
        except Exception as e:
            print(f"Validation error: {str(e)}")
            raise serializers.ValidationError(str(e))
    
    def create(self, validated_data):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            raise PermissionDenied("Authentication required.")

        if request.user.user_type != 'patient':
            raise PermissionDenied("Only patients can book appointments.")

        try:
            appointment_date = validated_data['appointment_date']
            appointment_time = validated_data['appointment_time']
            naive_datetime = datetime.combine(appointment_date, appointment_time)
            validated_data['patient'] = request.user

            print("Creating appointment with data:", validated_data)
            return super().create(validated_data)
        except Exception as e:
            import traceback
            print("Error creating appointment:", str(e))
            traceback.print_exc()
            raise serializers.ValidationError(f"Failed to create appointment: {str(e)}")