from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework import serializers
from .models import User, OTPVerification
import random
import string
from datetime import timedelta
import os


def generate_otp():
    return "".join(random.choices(string.digits, k=6))


class SignupRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def create(self, validated_data):
        email = validated_data["email"].lower()
        otp_expiry = int(os.getenv("OTP_EXPIRY_MINUTES", "5"))
        cooldown = int(os.getenv("OTP_RESEND_COOLDOWN_SECONDS", "30"))
        otp_obj, created = OTPVerification.objects.get_or_create(email=email, defaults={
            "code": generate_otp(),
            "expires_at": timezone.now() + timedelta(minutes=otp_expiry),
        })
        if not created:
            if not otp_obj.can_resend(cooldown):
                raise serializers.ValidationError({"detail": "Please wait before requesting another OTP"})
            otp_obj.code = generate_otp()
            otp_obj.expires_at = timezone.now() + timedelta(minutes=otp_expiry)
            otp_obj.attempts = 0
            otp_obj.last_sent_at = timezone.now()
            otp_obj.verified = False
            otp_obj.save()
        else:
            otp_obj.last_sent_at = timezone.now()
            otp_obj.save()
        return otp_obj


class OTPVerifySerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(min_length=6, max_length=6)

    def validate(self, attrs):
        email = attrs["email"].lower()
        code = attrs["code"]
        otp_obj = OTPVerification.objects.filter(email=email).first()
        if not otp_obj:
            raise serializers.ValidationError({"detail": "No OTP found for this email"})
        if otp_obj.is_expired():
            raise serializers.ValidationError({"detail": "OTP expired"})
        max_attempts = int(os.getenv("OTP_MAX_ATTEMPTS", "3"))
        if otp_obj.attempts >= max_attempts:
            raise serializers.ValidationError({"detail": "Max attempts reached"})
        if otp_obj.code != code:
            otp_obj.attempts += 1
            otp_obj.save()
            raise serializers.ValidationError({"detail": "Invalid OTP"})
        attrs["otp_obj"] = otp_obj
        return attrs

    def create(self, validated_data):
        otp_obj = validated_data["otp_obj"]
        otp_obj.verified = True
        otp_obj.save()
        return otp_obj


class SetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8)

    def create(self, validated_data):
        email = validated_data["email"].lower()
        otp_obj = OTPVerification.objects.filter(email=email, verified=True).first()
        if not otp_obj:
            raise serializers.ValidationError({"detail": "OTP not verified"})
        user, _ = User.objects.get_or_create(email=email)
        user.set_password(validated_data["password"])
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get("email").lower()
        password = attrs.get("password")
        user = authenticate(email=email, password=password)
        if not user:
            raise serializers.ValidationError({"detail": "Invalid credentials"})
        attrs["user"] = user
        return attrs