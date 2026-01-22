from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework.serializers import (
    ModelSerializer,
    IntegerField,
    FloatField,
    SerializerMethodField,
    CharField,
    Serializer,
)

from .models import (
    Product,
    Tag,
    Review,
    Image,
    Category,
    Specification,
    BasketItem,
)


class ErrorSerializer(Serializer):
    error = CharField(default="Bad Request")


class SuccessSerializer(Serializer):
    message = CharField(default="successful operation")


class TagsSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = "id", "name"


class ReviewsSerializer(ModelSerializer):
    class Meta:
        model = Review
        fields = "author", "email", "text", "rate"


class ImagesSerializer(ModelSerializer):
    class Meta:
        model = Image
        fields = "src", "alt"


class SpecificationSerializer(ModelSerializer):
    class Meta:
        model = Specification
        fields = "name", "value"


class CatalogSerializer(ModelSerializer):
    tags = TagsSerializer(many=True, read_only=True)
    reviews = IntegerField(read_only=True)  # количество отзывов
    rating = FloatField(read_only=True)  # средний рейтинг
    images = ImagesSerializer(many=True, source="image_set", read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "title",
            "description",
            "price",
            "count",
            "freeDelivery",
            "date",
            "tags",
            "category",
            "rating",
            "reviews",
            "images",
        )


class ProductSerializer(ModelSerializer):
    reviews = ReviewsSerializer(many=True, source="review_set", read_only=True)
    rating = FloatField(read_only=True)
    images = ImagesSerializer(many=True, source="image_set", read_only=True)
    tags = SerializerMethodField()
    specifications = SpecificationSerializer(
        many=True, source="specification_set", read_only=True
    )
    price = SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "id",
            "title",
            "description",
            "fullDescription",
            "price",
            "count",
            "freeDelivery",
            "date",
            "tags",
            "category",
            "rating",
            "reviews",
            "images",
            "specifications",
        )

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_tags(self, obj):
        if obj.tags:
            tags = TagsSerializer(obj.tags, many=True)
            return [{"id": tag["id"], "name": tag["name"]} for tag in tags.data]
        return None

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_price(self, obj):
        now = timezone.now()
        if obj.dateFrom and obj.dateTo:
            if obj.dateFrom <= now and obj.dateTo >= now:
                return obj.salePrice
        return obj.price


class SubcategoriesSerializer(ModelSerializer):
    image = SerializerMethodField()

    class Meta:
        model = Category
        fields = "id", "title", "image"

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_image(self, obj):
        if obj.image:
            return {"src": obj.image.url, "alt": obj.title}
        return None


class CategoriesSerializer(ModelSerializer):
    subcategories = SerializerMethodField()
    image = SerializerMethodField()

    class Meta:
        model = Category
        fields = "id", "title", "image", "subcategories"

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_image(self, obj):
        if obj.image:
            return {"src": obj.image.url, "alt": obj.title}
        return None

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_subcategories(self, obj):
        result = Category.objects.filter(parent_id=obj.pk).all()
        return SubcategoriesSerializer(result, many=True).data


class BannerSerializer(ModelSerializer):
    images = SerializerMethodField()
    title = SerializerMethodField()

    class Meta:
        model = Product
        fields = (
            "category",
            "title",
            "price",
            "images",
        )

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_title(self, obj):
        return obj.category.title if obj.category else None

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_images(self, obj):
        if obj.category:
            return [{"src": obj.category.image.url, "alt": obj.category.title}]
        return None


class ProductsHomePageSerializer(ModelSerializer):
    images = ImagesSerializer(many=True, source="image_set", read_only=True)

    class Meta:
        model = Product
        fields = (
            "id",
            "title",
            "price",
            "images",
            "sortIndex",
            "limitedEdition",
        )


class BasketItemSerializer(ModelSerializer):
    id = IntegerField(source="product.id", read_only=True)
    images = ImagesSerializer(source="product.image_set", many=True, read_only=True)
    title = CharField(source="product.title", read_only=True)
    price = SerializerMethodField()

    class Meta:
        model = BasketItem
        fields = ("id", "title", "price", "images", "count")

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_price(self, obj):
        now = timezone.now()
        if obj.product.dateFrom and obj.product.dateTo:
            if obj.product.dateFrom <= now and obj.product.dateTo >= now:
                return obj.product.salePrice
        return obj.product.price


class AddDeleteBasketSerializer(Serializer):
    id = IntegerField(help_text="ID элемента в корзине")
    count = IntegerField(
        help_text="Количество для удаления/добавления", required=True, min_value=1
    )


class SalesSerializer(ModelSerializer):
    images = ImagesSerializer(many=True, source="image_set", read_only=True)
    dateFrom = SerializerMethodField()
    dateTo = SerializerMethodField()

    class Meta:
        model = Product
        fields = ("id", "title", "price", "images", "salePrice", "dateFrom", "dateTo")

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_dateFrom(self, obj):
        return obj.dateFrom.strftime("%d-%m") if obj.dateFrom else None

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_dateTo(self, obj):
        return obj.dateTo.strftime("%d-%m") if obj.dateTo else None
