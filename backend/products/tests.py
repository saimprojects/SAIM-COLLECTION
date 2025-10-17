from django.urls import reverse
from rest_framework.test import APITestCase
from .models import Product


class ProductTests(APITestCase):
    def setUp(self):
        Product.objects.create(title="Test Product", description="Desc", price=10.0, is_active=True)

    def test_list_products(self):
        resp = self.client.get(reverse("product_list"))
        self.assertEqual(resp.status_code, 200)
        self.assertGreaterEqual(len(resp.data), 1)

    def test_detail_product(self):
        p = Product.objects.first()
        resp = self.client.get(reverse("product_detail", args=[p.slug]))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["slug"], p.slug)