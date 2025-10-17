from django.urls import reverse
from rest_framework.test import APITestCase
from .models import OTPVerification, User


class OTPFlowTests(APITestCase):
    def test_signup_otp_flow(self):
        email = "test@example.com"
        # request otp
        resp = self.client.post(reverse("signup_request_otp"), {"email": email})
        self.assertEqual(resp.status_code, 200)
        otp = OTPVerification.objects.get(email=email)
        # verify wrong code fails
        resp = self.client.post(reverse("signup_verify_otp"), {"email": email, "code": "000000"})
        self.assertEqual(resp.status_code, 400)
        # verify correct code
        resp = self.client.post(reverse("signup_verify_otp"), {"email": email, "code": otp.code})
        self.assertEqual(resp.status_code, 200)
        # set password
        resp = self.client.post(reverse("signup_set_password"), {"email": email, "password": "password123"})
        self.assertEqual(resp.status_code, 200)
        # login
        resp = self.client.post(reverse("login"), {"email": email, "password": "password123"})
        self.assertEqual(resp.status_code, 200)
        self.assertIn("access", resp.data)