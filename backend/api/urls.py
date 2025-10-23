from django.urls import path
from .views import UploadAnalyzeView, ImageAssetDetailView

urlpatterns = [
    path("upload/", UploadAnalyzeView.as_view(), name="upload"),
    path("images/<int:pk>/", ImageAssetDetailView.as_view(), name="image-detail"),
]