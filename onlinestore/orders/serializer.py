from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework.fields import IntegerField, SerializerMethodField
from rest_framework.serializers import ModelSerializer, Serializer, CharField

from catalog.models import Product, Image, Basket
from .models import Order


class OrderSerializer(ModelSerializer):
    class Meta:
        model = Order
        fields = (
            "id",
            "deliveryType",
            "paymentType",
            "totalCost",
            "status",
        )


class ErrorSerializer(Serializer):
    error = CharField(default="Bad Request")


class SuccessSerializer(Serializer):
    message = CharField(default="successful operation")


class CreateOrderSerializer(Serializer):
    id = IntegerField(help_text="id заказа", default=1)
    price = IntegerField(help_text="стоимость товара", default=0)
    count = IntegerField(help_text="количество товара", default=1)


class OrderCreatedSerializer(Serializer):
    orderId = IntegerField(help_text="id заказа", default=123)


class ImagesSerializer(ModelSerializer):
    class Meta:
        model = Image
        fields = "src", "alt"


class ProductSerializer(ModelSerializer):
    images = ImagesSerializer(many=True, source="image_set", read_only=True)
    price = SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "title",
            "description",
            "price",
            "count",
            "images",
        )

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_price(self, obj):
        now = timezone.now()
        if obj.dateFrom and obj.dateTo:
            if obj.dateFrom <= now and obj.dateTo >= now:
                return obj.salePrice
        return obj.price


class GetOrderSerializer(ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "fullName",
            "email",
            "phone",
            "deliveryType",
            "paymentType",
            "totalCost",
            "status",
            "city",
            "address",
            "products",
        )


class ProductIConfirmedSerializer(Serializer):
    id = IntegerField(help_text="id заказа", default=1)
    price = IntegerField(help_text="стоимость товара", default=0)
    count = IntegerField(help_text="количество товара", default=1)


class OrderConfirmedSerializer(Serializer):
    address = CharField(default="Адрес доставки")
    city = CharField(default="Город")
    deliveryType = CharField(default="Тип доставки")
    email = CharField(default="asd@email.com")
    fullName = CharField(default="имярек")
    phone = CharField(default="88003004444")
    paymentType = CharField(default="способ оплаты")
    products = ProductIConfirmedSerializer(many=True)


class PaymentSerializer(Serializer):
    name = CharField(default="Полное имя")
    number = IntegerField(help_text="номер карты", default="9999999999999999")
    year = IntegerField(help_text="год завершения действия карты", default="2035")
    month = IntegerField(help_text="месяц завершения действия карты", default="05")
    code = IntegerField(help_text="CVV карты", default="247")
