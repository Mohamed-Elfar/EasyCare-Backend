from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('national_id', 'email', 'full_name', 'user_type', 'account_status', 'is_staff', 'is_superuser')
    search_fields = ('national_id', 'email', 'full_name')
    ordering = ('national_id',)
    fieldsets = (
        (None, {'fields': (
            'national_id', 'email', 'phone_number', 'password', 'full_name', 'gender', 'birthday', 'address',
            'user_type', 'account_status', 'hospital', 'clinic', 'specialization', 'pharmacy_name', 'pharmacy_address',
            'face_id_image', 'back_id_image', 'is_staff', 'is_superuser'
        )}),
    )
    add_fieldsets = (
        (None, {'fields': (
            'national_id', 'email', 'phone_number', 'password', 'full_name', 'gender', 'birthday', 'address',
            'user_type', 'account_status', 'hospital', 'clinic', 'specialization', 'pharmacy_name', 'pharmacy_address',
            'face_id_image', 'back_id_image', 'is_staff', 'is_superuser'
        )}),
    )
    filter_horizontal = ()
    list_filter = ('user_type', 'account_status', 'is_staff', 'is_superuser')