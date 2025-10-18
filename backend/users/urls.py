from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    SignupRequestOTPView,
    VerifyOTPView,
    SetPasswordView,
    LoginView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
)

urlpatterns = [
    path("signup/request-otp/", SignupRequestOTPView.as_view(), name="signup_request_otp"),
    path("signup/verify-otp/", VerifyOTPView.as_view(), name="signup_verify_otp"),
    path("signup/set-password/", SetPasswordView.as_view(), name="signup_set_password"),
    path("login/", LoginView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("password/reset/", PasswordResetRequestView.as_view(), name="password_reset"),
    path("password/reset/confirm/", PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
]