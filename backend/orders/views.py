from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from products.models import Product
from .models import Order, DownloadLink
from .serializers import OrderSerializer, CreateOrderSerializer


class CreateOrderView(generics.CreateAPIView):
    serializer_class = CreateOrderSerializer
    permission_classes = [permissions.IsAuthenticated]


class MyOrdersView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by("-created_at")


class DownloadLinkView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, link_id):
        link = get_object_or_404(DownloadLink, id=link_id, order__user=request.user)
        if not link.is_valid():
            return Response({"detail": "Link expired or download limit reached"}, status=status.HTTP_410_GONE)
        link.register_download()
        # Redirect to the actual URL
        return redirect(link.url)