from io import TextIOWrapper
from csv import DictReader

from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.db.models import QuerySet
from django.shortcuts import render, redirect
from django.urls import path

from catalog.models import Product
from .models import Order


# регистрация связанных данных для поля 'Order' для админки, полученное через many_to_many c 'Product'
class ProductsInline(admin.TabularInline):
    # class ProductInline(admin.StackedInline):
    model = Order.products.through


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    inlines = [
        ProductsInline
    ]  # создание поля для Inline объектов в админке в разделе Orders
    list_display = [
        "pk",
        "fullName",
        "email",
        "phone",
        "deliveryType",
        "paymentType",
        "totalCost",
        "status",
        "city",
        "address",
        "user_",
        "paymentError",
    ]
    list_display_links = list_display

    def get_queryset(self, request):
        return Order.objects.select_related("user").prefetch_related("products")

    def user_(self, obj: Order) -> str:
        return obj.user.first_name or obj.user.username
