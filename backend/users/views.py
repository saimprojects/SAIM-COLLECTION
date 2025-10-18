import os
from django.core.mail import send_mail
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import SignupRequestSerializer, OTPVerifySerializer, SetPasswordSerializer, LoginSerializer
from .throttles import OTPThrottle
from .models import EmailLog, User


class SignupRequestOTPView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [OTPThrottle]

    def post(self, request):
        serializer = SignupRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp_obj = serializer.save()

        subject = "Your OTP Code"
        body = f"Your verification code is {otp_obj.code}. It expires in {os.getenv('OTP_EXPIRY_MINUTES', '5')} minutes."
        try:
            send_mail(subject, body, os.getenv("DEFAULT_FROM_EMAIL", "noreply@example.com"), [otp_obj.email])
            EmailLog.objects.create(to_email=otp_obj.email, subject=subject, body=body, success=True)
        except Exception as e:
            EmailLog.objects.create(to_email=otp_obj.email, subject=subject, body=body, success=False, error=str(e))

        return Response({"detail": "OTP sent"}, status=status.HTTP_200_OK)


class VerifyOTPView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [OTPThrottle]

    def post(self, request):
        serializer = OTPVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "OTP verified"}, status=status.HTTP_200_OK)


class SetPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = SetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"detail": "Password set. You can now login."}, status=status.HTTP_200_OK)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        refresh = RefreshToken.for_user(user)
        return Response({"access": str(refresh.access_token), "refresh": str(refresh)}, status=status.HTTP_200_OK)


class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email", "").lower()
        user = User.objects.filter(email=email).first()
        if not user:
            return Response({"detail": "If the email exists, a reset link has been sent."}, status=status.HTTP_200_OK)
        token = PasswordResetTokenGenerator().make_token(user)
        reset_link = f"http://localhost:5173/forgot-password?email={email}&token={token}"
        subject = "Password Reset"
        body = f"Click the link to reset your password: {reset_link}"
        try:
            send_mail(subject, body, os.getenv("DEFAULT_FROM_EMAIL", "noreply@example.com"), [email])
            EmailLog.objects.create(to_email=email, subject=subject, body=body, success=True)
        except Exception as e:
            EmailLog.objects.create(to_email=email, subject=subject, body=body, success=False, error=str(e))
        return Response({"detail": "If the email exists, a reset link has been sent."}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email", "").lower()
        token = request.data.get("token", "")
        new_password = request.data.get("new_password", "")
        user = get_object_or_404(User, email=email)
        if not PasswordResetTokenGenerator().check_token(user, token):
            return Response({"detail": "Invalid or expired token"}, status=status.HTTP_400_BAD_REQUEST)
        if len(new_password) < 8:
            return Response({"detail": "Password too short"}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(new_password)
        user.save()
        return Response({"detail": "Password reset successful"}, status=status.HTTP_200_OK)