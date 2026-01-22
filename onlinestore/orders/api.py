import json

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Order
from .serializer import (
    OrderSerializer,
    CreateOrderSerializer,
    GetOrderSerializer,
    OrderCreatedSerializer,
    ErrorSerializer,
    SuccessSerializer,
    OrderConfirmedSerializer,
    PaymentSerializer,
)

from catalog.models import Basket


class OrdersAPIView(APIView):
    """
    Получить/изменить/удалить корзину продуктов
    """

    @extend_schema(
        description="Get active orders",
        tags=["order"],
        responses={200: OrderSerializer, 400: ErrorSerializer},
    )
    def get(self, request, *args):
        orders = (
            Order.objects.defer(
                "createdAt", "fullName", "email", "phone", "city", "address"
            )
            .filter(user=request.user)
            .order_by("-createdAt")
        )
        result = list(OrderSerializer(orders, many=True).data)
        return Response(result)

    @extend_schema(
        description="Create order",
        tags=["order"],
        request=CreateOrderSerializer,
        responses={200: OrderCreatedSerializer, 400: ErrorSerializer},
    )
    def post(self, request, *args):
        data = request.data
        total_cost = 0
        order = Order.objects.create(user=request.user, totalCost=total_cost)

        for item in data:
            total_cost += item["count"] * item["price"]
            order.products.add(item["id"], through_defaults={"count": item["count"]})

        order.save()
        return Response({"orderId": order.pk})


@extend_schema(
    description="Get order",
    tags=["order"],
    responses={200: GetOrderSerializer, 400: ErrorSerializer},
)
class GetOrderAPIView(APIView):
    def get(self, request, id=None, format=None):
        order = get_object_or_404(
            Order.objects.defer("createdAt").prefetch_related("products"), pk=id
        )
        prodicts_in_order = order.product_items.all()
        prods = {}
        for item in prodicts_in_order:
            prods.update({item.product_id: item.count})
        serializer = GetOrderSerializer(order)
        result = serializer.data
        for item in result["products"]:
            item["count"] = prods[item["id"]]
        return Response(result)

    @extend_schema(
        description="Confirm order",
        tags=["order"],
        request=OrderConfirmedSerializer,
        responses={200: SuccessSerializer, 400: ErrorSerializer},
    )
    def post(self, request, id=None, format=None):
        data = request.data
        fields = [
            "address",
            "city",
            "deliveryType",
            "email",
            "fullName",
            "phone",
            "paymentType",
        ]
        order = get_object_or_404(Order.objects, pk=data["orderId"])

        # если заказ завершен успешно
        if order.status == "completed":
            return Response({"orderId": None})

        for field in fields:
            if data[field]:
                setattr(order, field, data[field])
        order.totalCost = sum(
            [item["count"] * item["price"] for item in data["products"]]
        )
        order.status = "confirmed"
        order.save()

        basket = Basket.objects.get(user=request.user)
        basket.items.all().delete()

        return Response({"orderId": id})


@extend_schema(
    description="make payment",
    tags=["payment"],
    request=PaymentSerializer,
    responses={200: SuccessSerializer, 400: ErrorSerializer},
)
class PaymentAPIView(APIView):
    def post(self, request, id=None, format=None):
        data = request.data
        paymentData = json.dumps(data)
        order = get_object_or_404(Order.objects, pk=id)
        order.status = "completed"
        order.paymentData = paymentData
        order.save()
        return Response({"message": "successful operation"})
