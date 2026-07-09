from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView

from .swagger_schemas import (
    orders_schema,
    create_order_schema,
    order_schema,
    order_confirmed_schema,
    payment_schema,
)
from .services import OrderService


class OrdersAPIView(APIView):
    @extend_schema(**orders_schema)
    def get(self, request, *args):
        """Получить все заказы"""
        return OrderService.get_orders(request)

    @extend_schema(**create_order_schema)
    def post(self, request, *args):
        """Создать заказ"""
        return OrderService.add_order(request)


@extend_schema(**order_schema)
class GetOrderAPIView(APIView):
    def get(self, request, id=None, format=None):
        """Получить ордер по id"""
        return OrderService.get_order(id)

    @extend_schema(**order_confirmed_schema)
    def post(self, request, id=None, format=None):
        """Подтвердить заказ"""
        return OrderService.order_confirme(request, id)


@extend_schema(**payment_schema)
class PaymentAPIView(APIView):
    def post(self, request, id=None, format=None):
        """Оформить платёж"""
        return OrderService.make_payment(request, id)
