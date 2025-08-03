from django.contrib import admin
from .models import DoctorSchedule, Appointment, DoctorDayOff


@admin.register(DoctorSchedule)
class DoctorScheduleAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'get_day_name', 'start_time', 'end_time', 'is_working_day', 'appointment_duration']
    list_filter = ['day_of_week', 'is_working_day']
    search_fields = ['doctor__full_name', 'doctor__specialization']
    ordering = ['doctor', 'day_of_week']
    
    def get_day_name(self, obj):
        return dict(DoctorSchedule.WEEKDAYS)[obj.day_of_week]
    get_day_name.short_description = 'Day'


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'appointment_date', 'appointment_time', 'status', 'created_at']
    list_filter = ['status', 'appointment_date', 'doctor__specialization']
    search_fields = ['patient__full_name', 'doctor__full_name', 'patient__national_id']
    ordering = ['-appointment_date', '-appointment_time']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Appointment Details', {
            'fields': ('patient', 'doctor', 'appointment_date', 'appointment_time', 'status')
        }),
        ('Notes', {
            'fields': ('notes', 'doctor_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DoctorDayOff)
class DoctorDayOffAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'date', 'reason', 'created_at']
    list_filter = ['date']
    search_fields = ['doctor__full_name', 'reason']
    ordering = ['-date']
