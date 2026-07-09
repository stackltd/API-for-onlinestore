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


orders_schema = dict(
    description="Get active orders",
    tags=["order"],
    responses={200: OrderSerializer, 400: ErrorSerializer},
)

create_order_schema = dict(
    description="Create order",
    tags=["order"],
    request=CreateOrderSerializer,
    responses={200: OrderCreatedSerializer, 400: ErrorSerializer},
)

order_schema = dict(
    description="Get order",
    tags=["order"],
    responses={200: GetOrderSerializer, 400: ErrorSerializer},
)

order_confirmed_schema = dict(
    description="Confirm order",
    tags=["order"],
    request=OrderConfirmedSerializer,
    responses={200: SuccessSerializer, 400: ErrorSerializer},
)

payment_schema = dict(
    description="make payment",
    tags=["payment"],
    request=PaymentSerializer,
    responses={200: SuccessSerializer, 400: ErrorSerializer},
)
