import os

from django.contrib.admin import StackedInline, ModelAdmin
from django.contrib import admin
from django.db.models import QuerySet
from django.http import HttpRequest

from .models import Product, Image, Tag, Review, Category, Specification


class ImagesInline(StackedInline):
    model = Image
    classes = ["collapse"]


class ReviewsInline(StackedInline):
    model = Review
    classes = ["collapse"]


class SpecificationInline(StackedInline):
    model = Specification
    classes = ["collapse"]


@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ["id", "title", "products_count", "parent", "is_root"]
    list_display_links = list_display

    fields = ["title", "image", "parent"]
    readonly_fields = ["products_count"]

    def products_count(self, obj):
        count = obj.products.count()
        return f"{count} товаров"

    products_count.short_description = "Товаров"

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj:
            form.base_fields["parent"].queryset = Category.objects.exclude(pk=obj.pk)
        return form


@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display = (
        "pk",
        "title",
        "category",
        "fullDescription",
        "price",
        "count",
        "freeDelivery",
        "archived",
    )

    list_display_links = ["pk", "title", "category", "fullDescription"]
    actions = ["mark_archived", "mark_unarchived"]

    # создание поля для Inline объектов в админке в разделе Products
    inlines = [ImagesInline, ReviewsInline, SpecificationInline]

    # задать список блоков полей описания продукта при переходе на него.
    # collapse - свернутое поле
    # description - описание блока
    fieldsets = [
        (
            "Product Description",
            {"fields": ("title", "description", "fullDescription")},
        ),
        (
            "Inventory options",
            {"fields": ("price", "count", "freeDelivery")},
        ),
        (
            "tags, category",
            {"fields": ("tags", "category")},
        ),
        (
            "sales",
            {
                "fields": ("salePrice", "dateFrom", "dateTo"),
                "classes": ("collapse",),
            },
        ),
        (
            "Extra",
            {
                "fields": ("archived", "sortIndex", "limitedEdition"),
                "classes": ("collapse",),
                "description": "Extra options. Field 'archived' is for soft delete",
            },
        ),
    ]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "category":
            # Показываем только ДОЧЕРНИЕ категории для продуктов
            kwargs["queryset"] = Category.objects.filter(parent__isnull=False)
            kwargs["help_text"] = "Выберите дочернюю категорию"
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

    def mark_unarchived(self, request: HttpRequest, queryset: QuerySet):
        queryset.update(archived=False)

    def mark_archived(self, request: HttpRequest, queryset: QuerySet):
        queryset.update(archived=True)

    def save_formset(self, request, form, formset, change):
        """
        Удаление файлов с диска при удалении соответствующих данных с бд
        """
        if hasattr(formset, "model") and formset.model == Image:
            deleted_ids = []
            for deleted_form in formset.deleted_forms:
                if deleted_form.instance.pk:
                    image = deleted_form.instance
                    if image.src:
                        print(f"Удаляем файл Image #{image.pk}: {image.src.path}")
                        image.src.delete(save=False)
                    deleted_ids.append(image.pk)

            if deleted_ids:
                self.message_user(request, f"Удалены изображения ID: {deleted_ids}")
        super().save_formset(request, form, formset, change)

    mark_archived.short_description = "Архивировать"
    mark_unarchived.short_description = "Снять статус 'архивирован'"


@admin.register(Tag)
class TagAdmin(ModelAdmin):
    list_display = "pk", "name", "category"
    list_display_links = ["pk", "name"]


@admin.register(Review)
class ReviewAdmin(ModelAdmin):
    list_display = "id", "product", "author", "email", "text", "rate"
    list_display_links = ["id", "product", "author", "email"]


@admin.register(Specification)
class SpecificationAdmin(ModelAdmin):
    list_display = "id", "product", "name", "value"
    list_display_links = "id", "product"
