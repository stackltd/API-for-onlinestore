from django.contrib.auth.models import User
from django.db.models import (
    Model,
    TextField,
    DateTimeField,
    ForeignKey,
    ManyToManyField,
    PROTECT,
    EmailField,
    DecimalField,
    PositiveIntegerField,
    CASCADE,
    BooleanField,
)

from catalog.models import Product
from phonenumber_field.modelfields import PhoneNumberField


class Order(Model):
    user = ForeignKey(User, on_delete=PROTECT)
    products = ManyToManyField(Product, related_name="orders", through="OrderProduct")
    createdAt = DateTimeField(auto_now_add=True)
    fullName = TextField(max_length=500, blank=True)
    email = EmailField(null=False, blank=True)
    phone = PhoneNumberField(region=None, null=True, blank=True)
    deliveryType = TextField(default="ordinary")
    paymentType = TextField(default="online")
    totalCost = DecimalField(default=0, decimal_places=2, max_digits=12)
    status = TextField(blank=True, default="created")
    city = TextField(blank=True)
    address = TextField(blank=True)
    paymentData = TextField(blank=True)
    paymentError = BooleanField(default=False)


class OrderProduct(Model):  # промежуточная модель
    order = ForeignKey(Order, on_delete=PROTECT, related_name="product_items")
    product = ForeignKey(Product, on_delete=PROTECT, related_name="order_items")
    count = PositiveIntegerField(default=1)

    class Meta:
        db_table = "orders_order_products"
        unique_together = ("order", "product")
