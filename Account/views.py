from rest_framework import status, permissions, serializers
from rest_framework_simplejwt.views import TokenObtainPairView
from django.core.mail import send_mail
from django.utils.crypto import get_random_string
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import (
    CustomUserSerializer,
    CustomTokenObtainPairSerializer,
    RequestPasswordResetSerializer,
    VerifyOTPSerializer,
    SetNewPasswordSerializer,
    PatientSerializer,
    DoctorSerializer,
    PharmacistSerializer
)
from .models import CustomUser

# User Registration View
class UserRegistrationView(APIView):
    def post(self, request):
        data = request.data.copy()
        # Automatically activate patients
        if data.get('user_type') == 'patient':
            data['account_status'] = 'active'
        serializer = CustomUserSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": "User created"}, status=status.HTTP_201_CREATED)
        else:
            error_messages = [error for errors in serializer.errors.values() for error in errors]
            message = ', '.join(error_messages)
            return Response({"message": message}, status=status.HTTP_400_BAD_REQUEST)

# Custom Token Obtain Pair View
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)

# User Profile View
class UserProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = CustomUserSerializer(user)
        return Response(serializer.data)

    def put(self, request):
        user = request.user
        serializer = CustomUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'Profile updated'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Password Reset Views
User = get_user_model()

class RequestPasswordResetView(APIView):
    def post(self, request):
        serializer = RequestPasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({'error': 'User with this email does not exist.'}, status=status.HTTP_404_NOT_FOUND)

            otp = get_random_string(length=6, allowed_chars='1234567890')
            user.otp = otp
            user.otp_created_at = timezone.now()
            user.save()

            send_mail(
                'Password Reset OTP',
                f'Your OTP for password reset is {otp}.',
                settings.EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )

            return Response({'status': 'OTP sent to email.'}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPView(APIView):
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            otp = serializer.validated_data['otp']

            try:
                user = User.objects.get(email=email)
                if user.otp != otp:
                    return Response({'error': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)

                return Response({'status': 'OTP verified successfully.'}, status=status.HTTP_200_OK)

            except User.DoesNotExist:
                return Response({'error': 'User with this email does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SetNewPasswordView(APIView):
    def post(self, request):
        serializer = SetNewPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            new_password = serializer.validated_data['new_password']
            otp = serializer.validated_data['otp']

            try:
                user = User.objects.get(email=email)
                if user.otp != otp:
                    return Response({'error': 'Invalid OTP.'}, status=status.HTTP_400_BAD_REQUEST)

                user.set_password(new_password)
                user.otp = ''
                user.save()

                return Response({'status': 'Password updated successfully.'}, status=status.HTTP_200_OK)

            except User.DoesNotExist:
                return Response({'error': 'User with this email does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Patient Search View
class PatientSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, national_id):
        if request.user.user_type not in ['doctor', 'pharmacist']:
            return Response({'detail': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

        patient = get_object_or_404(CustomUser, national_id=national_id, user_type='patient')
        serializer = PatientSerializer(patient)
        return Response(serializer.data, status=status.HTTP_200_OK)

# Doctor and Pharmacist List Views
class DoctorListView(APIView):
    def get(self, request):
        doctors = CustomUser.objects.filter(user_type='doctor')
        serializer = DoctorSerializer(doctors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PharmacistListView(APIView):
    def get(self, request):
        pharmacists = CustomUser.objects.filter(user_type='pharmacist')
        serializer = PharmacistSerializer(pharmacists, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)











from rest_framework import generics, permissions
from .models import CustomUser
from .serializers import AccountStatusUpdateSerializer

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_staff or request.user.is_superuser

# class AccountStatusUpdateView(generics.UpdateAPIView):
#     queryset = CustomUser.objects.all()
#     serializer_class = AccountStatusUpdateSerializer
#     permission_classes = [permissions.IsAuthenticated, IsAdminUser]
#     lookup_field = 'id'

from django.core.mail import send_mail
from django.conf import settings

class AccountStatusUpdateView(generics.UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = AccountStatusUpdateSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    lookup_field = 'id'

    def perform_update(self, serializer):
        user = self.get_object()
        old_status = user.account_status
        instance = serializer.save()
        # If status changed to active, send email
        if old_status != 'active' and instance.account_status == 'active':
            send_mail(
                subject='Your CareSync. account is activated',
                message='Congratulations! Your account has been activated by the admin. You can now log in and use the platform.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.email],
                fail_silently=True,
            )
        # If status changed to rejected, send rejection email and delete user
        elif old_status != 'rejected' and instance.account_status == 'rejected':
            email = user.email
            send_mail(
                subject='Your CareSync account was rejected',
                message='Sorry, your account was rejected because some data is not valid. Please try again with valid data.',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=True,
            )
            user.delete()
        else:
            serializer.save()
from rest_framework import generics, permissions
from .models import CustomUser
from .serializers import AdminUserListSerializer
class AdminUserListView(generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = AdminUserListSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminUser]
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context