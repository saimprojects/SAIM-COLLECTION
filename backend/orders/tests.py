from django.urls import reverse
from rest_framework.test import APITestCase
from users.models import User
from products.models import Product
from .models import Order


class OrderTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="u@example.com", password="password123")
        self.product = Product.objects.create(title="P1", description="D", price=5.0, is_active=True)

    def authenticate(self):
        resp = self.client.post(reverse("login"), {"email": "u@example.com", "password": "password123"})
        token = resp.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_create_and_approve_order(self):
        self.authenticate()
        resp = self.client.post(reverse("create_order"), {"product": self.product.id})
        self.assertEqual(resp.status_code, 201)
        order = Order.objects.get(user=self.user, product=self.product)
        # approve
        order.approve(admin_user=self.user)
        # list orders
        resp = self.client.get(reverse("my_orders"))
        self.assertEqual(resp.status_code, 200)
        has_link = any(o.get("download_link") for o in resp.data)
        self.assertTrue(has_link)