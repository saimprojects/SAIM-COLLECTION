import uuid
from datetime import timedelta
import os

from django.conf import settings
from django.db import models
from django.utils import timezone
import cloudinary
import cloudinary.utils

from products.models import Product
from users.models import User


class Order(models.Model):
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="orders")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="approved_orders")
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def approve(self, admin_user=None):
        self.status = self.STATUS_APPROVED
        self.approved_by = admin_user
        self.approved_at = timezone.now()
        self.save()
        OrderLog.objects.create(order=self, action="approved", actor=admin_user)

        # Create download link
        expiry_days = 7
        max_downloads = 3
        DownloadLink.create_for_order(self, expiry_days=expiry_days, max_downloads=max_downloads)

    def reject(self, admin_user=None):
        self.status = self.STATUS_REJECTED
        self.approved_by = admin_user
        self.approved_at = timezone.now()
        self.save()
        OrderLog.objects.create(order=self, action="rejected", actor=admin_user)

    def __str__(self):
        return f"Order {self.id} - {self.user.email} - {self.product.title}"


class DownloadLink(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="download_link")
    url = models.URLField(blank=True)
    expires_at = models.DateTimeField()
    max_downloads = models.PositiveIntegerField(default=3)
    download_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    external_warning = models.BooleanField(default=False)

    @classmethod
    def create_for_order(cls, order: Order, expiry_days: int, max_downloads: int):
        expires_at = timezone.now() + timedelta(days=expiry_days)
        url = ""
        warning = False
        if order.product.file and order.product.file.name:
            # Cloudinary signed URL
            public_id = order.product.file.name
            # cloudinary.utils.cloudinary_url returns (url, options)
            url, _ = cloudinary.utils.cloudinary_url(
                public_id,
                sign_url=True,
                expires_at=int(expires_at.timestamp()),
                resource_type="raw",  # files uploaded to cloudinary_storage are usually 'raw'
            )
        elif order.product.external_link:
            url = order.product.external_link
            warning = True
        link = cls.objects.create(order=order, url=url, expires_at=expires_at, max_downloads=max_downloads, external_warning=warning)
        # Email user
        from django.core.mail import send_mail
        from users.models import EmailLog
        subject = "Your download link"
        body = f"Your download link for {order.product.title}: {url}\nThis link expires on {expires_at} and allows {max_downloads} downloads."
        try:
            send_mail(subject, body, os.getenv("DEFAULT_FROM_EMAIL", "noreply@example.com"), [order.user.email])
            EmailLog.objects.create(to_email=order.user.email, subject=subject, body=body, success=True)
        except Exception as e:
            EmailLog.objects.create(to_email=order.user.email, subject=subject, body=body, success=False, error=str(e))
        return link

    def is_valid(self):
        return self.download_count < self.max_downloads and timezone.now() < self.expires_at

    def register_download(self):
        self.download_count += 1
        self.save()

    def __str__(self):
        return f"Link for Order {self.order_id}"


class OrderLog(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="logs")
    action = models.CharField(max_length=50)
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order_id} - {self.action} - {self.timestamp}"