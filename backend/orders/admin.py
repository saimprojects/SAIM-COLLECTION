from django.contrib import admin
from .models import Order, DownloadLink, OrderLog


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "product", "status", "approved_by", "approved_at", "created_at")
    list_filter = ("status", "approved_at")
    search_fields = ("user__email", "product__title")
    actions = ["approve_orders", "reject_orders"]

    def approve_orders(self, request, queryset):
        for order in queryset.filter(status=Order.STATUS_PENDING):
            order.approve(admin_user=request.user)
    approve_orders.short_description = "Approve selected orders"

    def reject_orders(self, request, queryset):
        for order in queryset.filter(status=Order.STATUS_PENDING):
            order.reject(admin_user=request.user)
    reject_orders.short_description = "Reject selected orders"


@admin.register(DownloadLink)
class DownloadLinkAdmin(admin.ModelAdmin):
    list_display = ("order", "url", "expires_at", "max_downloads", "download_count", "external_warning")
    list_filter = ("expires_at", "external_warning")


@admin.register(OrderLog)
class OrderLogAdmin(admin.ModelAdmin):
    list_display = ("order", "action", "actor", "timestamp")
    list_filter = ("action", "timestamp")