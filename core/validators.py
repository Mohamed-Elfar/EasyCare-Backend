import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from rest_framework import serializers


def validate_password_strength(password):
    """
    Utility function to validate password strength.
    Can be used in both Django forms and DRF serializers.
    """
    errors = []
    
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long.")
    
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter.")
    
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter.")
    
    if not re.search(r'[0-9]', password):
        errors.append("Password must contain at least one digit.")
    
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:"\\|,.<>\/?]', password):
        errors.append("Password must contain at least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?).")
    
    return errors


class CustomPasswordValidator:
    """
    Validate that the password meets all requirements:
    - At least 8 characters long
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one digit
    - Contains at least one special character
    """
    
    def validate(self, password, user=None):
        errors = validate_password_strength(password)
        if errors:
            raise ValidationError(errors)
    
    def get_help_text(self):
        return _(
            "Your password must contain at least 8 characters, including uppercase and lowercase letters, "
            "at least one digit, and at least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)."
        )
