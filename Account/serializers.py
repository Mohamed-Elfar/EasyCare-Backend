from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import CustomUser
from Prescription.models import Prescription

class CustomUserSerializer(serializers.ModelSerializer):
    face_id_image = serializers.ImageField(required=False, allow_null=True)
    back_id_image = serializers.ImageField(required=False, allow_null=True)
    class Meta:
        model = CustomUser
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True},
            'phone_number': {'validators': []},
            'email': {'validators': []},
            'face_id_image': {'required': False, 'allow_null': True},
            'back_id_image': {'required': False, 'allow_null': True},
        }

    def validate_password(self, value):
        from core.validators import validate_password_strength
        
        errors = validate_password_strength(value)
        if errors:
            raise serializers.ValidationError(errors)
        
        return value

    def validate_national_id(self, value):
        if CustomUser.objects.filter(national_id=value).exists():
            raise serializers.ValidationError("National ID already exists.")
        return value

    def validate_phone_number(self, value):
        if CustomUser.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("Phone number already exists.")
        return value

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = CustomUser.objects.create(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        user_type = instance.user_type

        if user_type == 'patient':
            fields_to_remove = ['otp_created_at', 'otp', 'id', 'last_login', 'hospital', 'clinic', 'specialization',
                                'pharmacy_name', 'pharmacy_address']
        elif user_type == 'doctor':
            fields_to_remove = ['otp_created_at', 'otp', 'id', 'last_login', 'pharmacy_name', 'pharmacy_address',
                                'diabetes', 'heart_disease', 'allergies', 'other_diseases']
        elif user_type == 'pharmacist':
            fields_to_remove = ['otp_created_at', 'otp', 'id', 'last_login', 'hospital', 'clinic', 'specialization',
                                'diabetes', 'heart_disease', 'allergies', 'other_diseases']

        for field in fields_to_remove:
            representation.pop(field, None)

        return representation


class UserLoginSerializer(serializers.Serializer):
    national_id = serializers.CharField(max_length=14)
    password = serializers.CharField(max_length=128)

User = get_user_model()

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        return token

    def validate(self, attrs):
        national_id = attrs.get('national_id')
        password = attrs.get('password')

        user = User.objects.filter(national_id=national_id).first()
        if user is None or not user.check_password(password):
            raise serializers.ValidationError('Invalid credentials')
        if user.account_status != 'active':
            raise serializers.ValidationError('Account is not active. Please wait for admin verification.')

        data = super().validate(attrs)
        data.update({'user_type': user.user_type})
        return data


class RequestPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)


class SetNewPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(min_length=8)
    
    def validate_new_password(self, value):
        from core.validators import validate_password_strength
        
        errors = validate_password_strength(value)
        if errors:
            raise serializers.ValidationError(errors)
        
        return value


class NestedPrescriptionSerializer(serializers.ModelSerializer):
    doctor = serializers.CharField(source='doctor.full_name', read_only=True)

    class Meta:
        model = Prescription
        fields = ['medicine_name', 'dosage', 'instructions', 'created_at', 'doctor']
        read_only_fields = ['created_at', 'doctor']


class PatientSerializer(serializers.ModelSerializer):
    prescriptions = NestedPrescriptionSerializer(many=True, read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'full_name', 'national_id', 'email', 'phone_number', 'birthday', 'address',
            'diabetes', 'heart_disease', 'allergies', 'other_diseases', 'prescriptions'
        ]


class DoctorSerializer(serializers.ModelSerializer):
    face_id_image = serializers.ImageField(required=False, allow_null=True)
    back_id_image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = CustomUser
        fields = [
            'email', 'phone_number', 'full_name', 'hospital', 'specialization', 'clinic',
            'face_id_image', 'back_id_image'
        ]


class PharmacistSerializer(serializers.ModelSerializer):
    face_id_image = serializers.ImageField(required=False, allow_null=True)
    back_id_image = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = CustomUser
        fields = [
            'full_name', 'phone_number', 'email', 'pharmacy_name', 'pharmacy_address',
            'face_id_image', 'back_id_image'
        ]

        from rest_framework import serializers
from .models import CustomUser

class AccountStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['account_status']
        extra_kwargs = {
            'account_status': {'required': True}
        }


class AdminUserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            'id', 'national_id', 'email', 'phone_number', 'full_name', 'user_type',
            'account_status', 'face_id_image', 'back_id_image'
        ]

    def get_face_id_image(self, obj):
        request = self.context.get('request')
        if obj.face_id_image and hasattr(obj.face_id_image, 'url'):
            url = obj.face_id_image.url
            # Ensure /media/ is in the URL
            if not url.startswith('/media/'):
                url = '/media' + url if not url.startswith('/') else '/media' + url
            return request.build_absolute_uri(url) if request else url
        return None

    def get_back_id_image(self, obj):
        request = self.context.get('request')
        if obj.back_id_image and hasattr(obj.back_id_image, 'url'):
            url = obj.back_id_image.url
            # Ensure /media/ is in the URL
            if not url.startswith('/media/'):
                url = '/media' + url if not url.startswith('/') else '/media' + url
            return request.build_absolute_uri(url) if request else url
        return None
