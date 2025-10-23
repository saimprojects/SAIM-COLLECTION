from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator
from django.db.models import JSONField


class ImageAsset(models.Model):
    original_image_url = models.URLField(blank=True, null=True)
    local_image = models.ImageField(upload_to="uploads/", blank=True, null=True)
    width = models.PositiveIntegerField(default=0)
    height = models.PositiveIntegerField(default=0)
    elements = JSONField(default=list, blank=True)  # list of detected/editable elements
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def image_source_url(self):
        if self.original_image_url:
            return self.original_image_url
        if self.local_image:
            return self.local_image.url
        return ""

    def __str__(self):
        return f"ImageAsset {self.id}"