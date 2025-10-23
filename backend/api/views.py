import os
import tempfile
from typing import Any, Dict

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status

from .models import ImageAsset
from .serializers import ImageAssetSerializer
from .processing import pil_image_from_fileobj, analyze_image
from .cloud import upload_image


class UploadAnalyzeView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        if "image" not in request.FILES:
            return Response({"detail": "No image file provided with key 'image'."}, status=400)
        image_file = request.FILES["image"]
        pil_img = pil_image_from_fileobj(image_file)

        # Save locally first
        img_bytes = ContentFile(image_file.read() if hasattr(image_file, "read") else image_file)
        # Need to rewind if read
        try:
            image_file.seek(0)
        except Exception:
            pass

        asset = ImageAsset.objects.create()
        filename = f"uploads/{asset.id}_{image_file.name}"
        asset.local_image.save(filename, image_file, save=True)

        # Cloudinary upload if configured
        original_url = ""
        if settings.USE_CLOUDINARY:
            ok, url, err = upload_image(asset.local_image.path, public_id=f"imageasset_{asset.id}")
            if ok and url:
                original_url = url
                asset.original_image_url = url
                asset.save(update_fields=["original_image_url"])

        # Analyze
        analysis = analyze_image(pil_img)
        asset.width = analysis.get("width", 0)
        asset.height = analysis.get("height", 0)
        asset.elements = analysis.get("elements", [])
        asset.save()

        data = ImageAssetSerializer(asset).data
        # Ensure proper image URL reference
        data["image_url"] = asset.image_source_url()
        return Response(data, status=201)


class ImageAssetDetailView(APIView):
    def get(self, request, pk: int, *args, **kwargs):
        asset = get_object_or_404(ImageAsset, pk=pk)
        data = ImageAssetSerializer(asset).data
        data["image_url"] = asset.image_source_url()
        return Response(data)

    def put(self, request, pk: int, *args, **kwargs):
        asset = get_object_or_404(ImageAsset, pk=pk)
        elements = request.data.get("elements")
        if not isinstance(elements, list):
            return Response({"detail": "elements must be a list"}, status=400)
        asset.elements = elements
        asset.save(update_fields=["elements"])
        data = ImageAssetSerializer(asset).data
        data["image_url"] = asset.image_source_url()
        return Response(data)