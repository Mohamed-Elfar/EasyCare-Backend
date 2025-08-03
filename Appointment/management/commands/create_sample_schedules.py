from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import time, date, timedelta
from Account.models import CustomUser
from Appointment.models import DoctorSchedule, DoctorDayOff


class Command(BaseCommand):
    help = 'Create sample doctor schedules for testing'
    
    def handle(self, *args, **options):
        # Get all doctors
        doctors = CustomUser.objects.filter(user_type='doctor')
        
        if not doctors.exists():
            self.stdout.write(
                self.style.WARNING('No doctors found. Please create some doctor accounts first.')
            )
            return
        
        for doctor in doctors:
            self.stdout.write(f'Creating schedule for Dr. {doctor.full_name}...')
            
            # Create a sample weekly schedule
            # Monday to Friday: 9:00 AM - 5:00 PM
            weekdays = [0, 1, 2, 3, 4]  # Monday to Friday
            for day in weekdays:
                schedule, created = DoctorSchedule.objects.get_or_create(
                    doctor=doctor,
                    day_of_week=day,
                    defaults={
                        'start_time': time(9, 0),  # 9:00 AM
                        'end_time': time(17, 0),   # 5:00 PM
                        'is_working_day': True,
                        'appointment_duration': 30  # 30 minutes per appointment
                    }
                )
                if created:
                    day_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'][day]
                    self.stdout.write(f'  - Added {day_name} schedule')
            
            # Saturday: 9:00 AM - 1:00 PM (half day)
            schedule, created = DoctorSchedule.objects.get_or_create(
                doctor=doctor,
                day_of_week=5,  # Saturday
                defaults={
                    'start_time': time(9, 0),   # 9:00 AM
                    'end_time': time(13, 0),    # 1:00 PM
                    'is_working_day': True,
                    'appointment_duration': 30
                }
            )
            if created:
                self.stdout.write('  - Added Saturday schedule (half day)')
            
            # Sunday: Day off
            schedule, created = DoctorSchedule.objects.get_or_create(
                doctor=doctor,
                day_of_week=6,  # Sunday
                defaults={
                    'start_time': time(9, 0),
                    'end_time': time(17, 0),
                    'is_working_day': False,
                    'appointment_duration': 30
                }
            )
            if created:
                self.stdout.write('  - Added Sunday (day off)')
            
            # Add a sample day off (next Friday)
            next_friday = date.today()
            days_ahead = 4 - next_friday.weekday()  # Friday is weekday 4
            if days_ahead <= 0:  # Target day already happened this week
                days_ahead += 7
            next_friday += timedelta(days_ahead)
            
            day_off, created = DoctorDayOff.objects.get_or_create(
                doctor=doctor,
                date=next_friday,
                defaults={
                    'reason': 'Medical Conference'
                }
            )
            if created:
                self.stdout.write(f'  - Added day off on {next_friday} (Medical Conference)')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created sample doctor schedules!')
        )
