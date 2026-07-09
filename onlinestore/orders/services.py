import json

from rest_framework.response import Response

from .models import Order
from .serializer import (
    OrderSerializer,
    GetOrderSerializer,
)

from catalog.models import Basket
from onlinestore.dao import DAO


class OrderService:

    @classmethod
    def get_orders(cls, request):
        orders = DAO.search_object_by_fields(
            model=Order,
            defer=("createdAt", "fullName", "email", "phone", "city", "address"),
            filter={"user": request.user},
            order_by="-createdAt",
        )
        result = list(OrderSerializer(orders, many=True).data)
        return Response(result)

    @classmethod
    def add_order(cls, request):
        data = request.data
        total_cost = 0
        order = DAO.create_object(
            model=Order, data_dict=dict(user=request.user, totalCost=total_cost)
        )
        for item in data:
            total_cost += item["count"] * item["price"]
            order.products.add(item["id"], through_defaults={"count": item["count"]})

        order.save()
        return Response({"orderId": order.pk})

    @classmethod
    def get_order(cls, id):
        order = DAO.search_object_by_fields(
            model=Order,
            defer=("createdAt",),
            prefetch_related=("products",),
            get_object_or_404_params={"pk": id},
        )
        products_in_order = order.product_items.all()
        prods = {}
        for item in products_in_order:
            prods.update({item.product_id: item.count})
        serializer = GetOrderSerializer(order)
        result = serializer.data
        for item in result["products"]:
            item["count"] = prods[item["id"]]
        return Response(result)

    @classmethod
    def order_confirme(cls, request, id):
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
        order = DAO.search_object_by_fields(
            model=Order, get_object_or_404_params={"pk": data["orderId"]}
        )
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

    @classmethod
    def make_payment(cls, request, id):
        data = request.data
        paymentData = json.dumps(data)
        order = DAO.search_object_by_fields(
            model=Order, get_object_or_404_params={"pk": id}
        )
        order.status = "completed"
        order.paymentData = paymentData
        order.save()
        return Response({"message": "successful operation"})
