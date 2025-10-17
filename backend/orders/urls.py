from django.urls import path
from .views import CreateOrderView, MyOrdersView, DownloadLinkView

urlpatterns = [
    path("", MyOrdersView.as_view(), name="my_orders"),
    path("create/", CreateOrderView.as_view(), name="create_order"),
    path("download/<uuid:link_id>/", DownloadLinkView.as_view(), name="download_link"),
]