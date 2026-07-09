from drf_spectacular.types import OpenApiTypes

from drf_spectacular.utils import OpenApiParameter

from .serializers import (
    CatalogSerializer,
    TagsSerializer,
    CategoriesSerializer,
    BannerSerializer,
    ProductsHomePageSerializer,
    SalesSerializer,
    ProductSerializer,
    ReviewsSerializer,
    BasketItemSerializer,
    AddDeleteBasketSerializer,
    SuccessSerializer,
    ErrorSerializer,
)


catalog_schema = dict(
    description="get catalog items",
    tags=["catalog"],
    request=CatalogSerializer,
    responses={200: CatalogSerializer, 400: {"error": "Bad Request"}},
    parameters=[
        OpenApiParameter(
            name="filter[minPrice]",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Минимальная цена",
            default=0,
        ),
        OpenApiParameter(
            name="filter[maxPrice]",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Максимальная цена",
            default=500_000,
        ),
        OpenApiParameter(
            name="filter[name]",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="Поиск по названию (iregex)",
            default="",
        ),
        OpenApiParameter(
            name="filter[available]",
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
            description="Только в наличии",
            default=False,
        ),
        OpenApiParameter(
            name="filter[freeDelivery]",
            type=OpenApiTypes.BOOL,
            location=OpenApiParameter.QUERY,
            description="Бесплатная доставка",
            default=False,
        ),
        OpenApiParameter(
            name="sort",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            enum=["rating", "price", "reviews", "date"],
            description="Вид сортировки",
            default="price",
        ),
        OpenApiParameter(
            name="sortType",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            enum=["int", "dec"],
            description="Сортировка цены",
            default="int",
        ),
        OpenApiParameter(
            name="limit",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Максимальное количество товара на странице",
            default=20,
        ),
        OpenApiParameter(
            name="tags[]",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            description="Поиск по тегу",
            default="",
        ),
    ],
)

tags_schema = dict(
    description="tags",
    tags=["tags"],
    request=TagsSerializer,
    responses={200: TagsSerializer, 400: {"error": "Bad Request"}},
)

categories_schema = dict(
    description="get categories",
    tags=["catalog"],
    responses={200: CategoriesSerializer, 400: ErrorSerializer},
)

banners_schema = dict(
    description="get banner items",
    tags=["catalog"],
    request=BannerSerializer,
    responses={200: BannerSerializer, 400: {"error": "Bad Request"}},
)

products_popular_schema = dict(
    description="get catalog popular items",
    tags=["catalog"],
    request=ProductsHomePageSerializer,
    responses={200: ProductsHomePageSerializer, 400: {"error": "Bad Request"}},
)

products_limited_schema = products_popular_schema.copy()
products_limited_schema["description"] = "get catalog limited items"

sales_schema = dict(
    description="get sales items",
    tags=["catalog"],
    request=SalesSerializer,
    responses={200: SalesSerializer, 400: {"error": "Bad Request"}},
)

product_schema = dict(
    description="get product",
    tags=["product"],
    request=ProductSerializer,
    responses={200: ProductSerializer, 400: {"error": "Bad Request"}},
)

product_review_schema = dict(
    description="post product review",
    tags=["product"],
    request=ReviewsSerializer,
    responses={200: ReviewsSerializer, 400: {"error": "Bad Request"}},
)

get_basket_schema = dict(
    description="Get items in basket",
    tags=["basket"],
    request=BasketItemSerializer,
    responses={200: BasketItemSerializer, 400: {"error": "Bad Request"}},
)

add_basket_schema = dict(
    description="Add item to basket",
    tags=["basket"],
    request=AddDeleteBasketSerializer,
    responses={200: SuccessSerializer, 400: ErrorSerializer},
)

delete_basket_schema = add_basket_schema.copy()
delete_basket_schema["description"] = "Remove item from basket"
