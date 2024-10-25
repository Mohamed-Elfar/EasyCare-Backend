# utils.py

import random
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator

def generate_otp():
    return str(random.randint(100000, 999999))

def send_otp_email(email, otp):
    subject = 'Your OTP Code'
    message = f'Your OTP code is {otp}.'
    from_email = settings.EMAIL_HOST_USER
    send_mail(subject, message, from_email, [email])
