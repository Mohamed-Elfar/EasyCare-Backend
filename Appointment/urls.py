from django.urls import path
from .views import (
    AvailableDoctorsView, DoctorScheduleView, doctor_availability,
    BookAppointmentView, PatientAppointmentsView, DoctorAppointmentsView,
    AppointmentDetailView, DoctorScheduleManageView, DoctorDayOffView
)

urlpatterns = [
    # Patient endpoints
    path('doctors/', AvailableDoctorsView.as_view(), name='available-doctors'),
    path('doctors/<int:doctor_id>/schedule/', DoctorScheduleView.as_view(), name='doctor-schedule'),
    path('doctors/<int:doctor_id>/availability/', doctor_availability, name='doctor-availability'),
    path('book/', BookAppointmentView.as_view(), name='book-appointment'),
    path('my-appointments/', PatientAppointmentsView.as_view(), name='patient-appointments'),
    path('appointments/<int:pk>/', AppointmentDetailView.as_view(), name='appointment-detail'),
    
    # Doctor endpoints
    path('doctor/appointments/', DoctorAppointmentsView.as_view(), name='doctor-appointments'),
    path('doctor/schedule/', DoctorScheduleManageView.as_view(), name='doctor-schedule-manage'),
    path('doctor/days-off/', DoctorDayOffView.as_view(), name='doctor-days-off'),
    path('doctor/schedule/<int:pk>/', DoctorScheduleManageView.as_view(), name='doctor-schedule-detail'),
    
]
