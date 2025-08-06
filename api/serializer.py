from api.models import User, Profile
from django.core.mail import send_mail, get_connection
from django.utils.timezone import now, timedelta
from datetime import timedelta
import datetime


from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.conf import settings


class UserSerializer(serializers.ModelField):
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        token['full_name'] = user.profile.full_name
        token['username'] = user.username
        token['email'] = user.email
        token['bio'] = user.profile.bio
        token['verified'] = user.profile.verified

        return token
    

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only = True, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2']

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields does not match"}
            )
        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
        )
        user.set_password(validated_data['password'])
        user.save()

        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        
        email_backend = settings.EMAIL_HOST
        if not email_backend:
            # Если email не настроен, не отправляем OTP
            return value
        
        user.generate_otp()

        send_mail(
            "Password Reset OTP",
            f"Your OTP for password reset is {user.otp}",
            "noreply@example.com", 
            [user.email],
            fail_silently=False,
        )
        return value
    
    

class OTPVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

    def validate(self, data):
        try:
            user = User.objects.get(email=data["email"])
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "User not found."})
        
        # Проверка, заблокирован ли пользователь
        if user.is_blocked():
            remaining = (user.block_until - now()).total_seconds()
            raise serializers.ValidationError({
                "detail": f"Too many attempts. Try again in {int(remaining)} seconds."})
        
         # Проверка, если OTP уже истек
        if user.otp_exp is None or user.otp_exp < now():
            # Генерируем новый OTP, если предыдущий истек
            user.generate_otp()
            raise serializers.ValidationError({"otp": "OTP expired. A new OTP has been sent."})


        # Check if OTP is correct and not expired
        if user.otp != data["otp"]:
            user.increment_attempts()
            # После увеличения попыток, если лимит достигнут, пользователь заблокирован
            if user.otp_attempts >= user.max_try_top:
                raise serializers.ValidationError({
                    "otp": "Too many invalid attempts. You are temporarily blocked."})
            else:
                raise serializers.ValidationError({"otp": "Invalid OTP."})

        if user.otp_exp < now():  # OTP срок
            raise serializers.ValidationError({"otp": "OTP expired."})
        
        

        #OTP зарегестрирован
        user.otp_verified = True
        user.reset_attempts()
        user.save()

        return data




class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            user = User.objects.get(email=data["email"])
        except User.DoesNotExist:
            raise serializers.ValidationError({"email": "User not found."})

        # Check if OTP was verified
        if not user.otp_verified:
            raise serializers.ValidationError({"otp": "OTP verification required."})

        return data

    def save(self, **kwargs):
        user = User.objects.get(email=self.validated_data["email"])
        user.set_password(self.validated_data["new_password"])
        user.otp = None  # Clear OTP after successful reset
        user.otp_exp = None
        user.otp_verified = False  # Reset verification status
        user.save()
        return user
