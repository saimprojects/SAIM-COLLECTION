from django.contrib import admin
from .models import Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("title", "price", "is_active", "created_at")
    search_fields = ("title", "description", "slug")
    list_filter = ("is_active",)
    prepopulated_fields = {"slug": ("title",)}