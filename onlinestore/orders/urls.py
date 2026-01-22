from django.urls import path

from .api import OrdersAPIView, GetOrderAPIView, PaymentAPIView

app_name = "orders"

urlpatterns = [
    path("orders/", OrdersAPIView.as_view(), name="orders"),
    path("order/<int:id>/", GetOrderAPIView.as_view(), name="order-get"),
    path("payment/<int:id>/", PaymentAPIView.as_view(), name="payment"),
]
