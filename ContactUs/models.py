from django.conf import settings
from django.db import models

class ContactUs(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)  # Use AUTH_USER_MODEL for custom user
    name = models.CharField(max_length=255)
    national_id = models.CharField(max_length=14)
    message = models.TextField()

    def __str__(self):
        return f"Contact Us from {self.name} ({self.national_id})"
