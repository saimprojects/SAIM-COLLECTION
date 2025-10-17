from rest_framework import serializers
from .models import Order, DownloadLink


class OrderSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(source="product.title", read_only=True)
    product_slug = serializers.CharField(source="product.slug", read_only=True)
    download_link = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ["id", "product_title", "product_slug", "status", "approved_at", "download_link"]

    def get_download_link(self, obj: Order):
        link = getattr(obj, "download_link", None)
        if link and link.is_valid():
            return {
                "id": str(link.id),
                "expires_at": link.expires_at,
                "remaining_downloads": link.max_downloads - link.download_count,
                "external_warning": link.external_warning,
            }
        return None


class CreateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ["product"]

    def create(self, validated_data):
        user = self.context["request"].user
        return Order.objects.create(user=user, **validated_data)