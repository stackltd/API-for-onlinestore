from django.db.models import Count, Avg, Min, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.response import Response
from rest_framework.views import APIView


from .models import Product, Tag, Category, Review
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
    ImagesSerializer,
    SuccessSerializer,
    ErrorSerializer,
)
from .utils import products_home_page, change_basket, user_basket, anon_basket


@extend_schema(
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
class CatalogAPIView(APIView):
    """
    Получить каталог продуктов
    """

    def get(self, request, *args):
        query = dict(request.query_params)
        filter = {
            "name": "",
            "minPrice": "0",
            "maxPrice": "500000",
            "Delivery": "false",
            "available": "false",
            "currentPage": "1",
            "sort": "price",
            "sortType": "inc",
            "tags[]": "",
            "limit": "20",
            "category": "",
            "name_from_search": "",
        }
        # парсинг query, получение словаря параметров фильтрации и сортировки
        for point in query:
            if "filter[" in point:
                name = point.rstrip("]").lstrip("filter[")
            else:
                name = point
            filter.update({name: query[point][0]})

        order_param = filter.get("sort")
        _name = filter.get("name", "")
        __name = filter.get("name_from_search", "")

        name = _name if _name else __name

        tag_ids = []
        tag_id = filter.get("tags[]", "")
        if tag_id:
            tag_ids.append(tag_id)

        # вычисление списка родительских, или дочерних категорий для product
        category_id = filter["category"]
        cat_sub_ids = []
        if category_id:
            # При parent_id=None получаем родительские категории
            parent_id = Category.objects.filter(id=category_id).first().parent_id
            cat_sub_ids = [
                obj.pk
                for obj in Category.objects.filter(
                    **({"id": category_id} if parent_id else {}),
                    **({"parent_id": category_id} if not parent_id else {}),
                ).all()
            ]
        # получаем продукты со связанными таблицами и агрегированными данными, производим сортировку и фильтрацию
        products = (
            Product.objects.defer(
                "created_by", "archived", "fullDescription", "sortIndex"
            )
            .prefetch_related("tags", "review_set", "image_set")
            .select_related("category")
            .annotate(
                reviews=Count("review"),
                rating=Avg("review__rate"),
            )
            .filter(
                archived=False,
                price__gte=filter["minPrice"],
                price__lte=filter["maxPrice"],
                **({"category__id__in": cat_sub_ids} if cat_sub_ids else {}),
                **({"tags__id__in": tag_ids} if tag_ids else {}),
                **({"title__iregex": name} if name else {}),
                **({"count__gt": 0} if filter["available"] == "true" else {}),
                **({"freeDelivery": True} if filter["Delivery"] == "true" else {}),
            )
            .order_by(
                f"-{order_param}" if filter["sortType"] == "inc" else f"{order_param}"
            )
        ).all()
        serializer = CatalogSerializer(products, many=True)

        # вычисление параметров пагинации
        currentPage = int(filter.get("currentPage", 1))
        result = list(serializer.data)
        numbers = len(result)
        # limit = int(filter.get("limit", 20))
        limit = 8
        lastPage = numbers // limit

        if numbers % limit:
            lastPage += 1

        start = (currentPage - 1) * limit
        stop = start + limit

        return Response(
            {
                "items": result[start:stop],
                "currentPage": currentPage,
                "lastPage": lastPage,
            }
        )


@extend_schema(
    description="tags",
    tags=["tags"],
    request=TagsSerializer,
    responses={200: TagsSerializer, 400: {"error": "Bad Request"}},
)
class TagsAPIView(APIView):
    def get(self, request, *args):
        query = dict(request.query_params)
        category_id = query.get("category", [None])[0]
        tags = (
            Tag.objects.select_related("category")
            .filter(
                **({"category__id__in": [category_id]} if category_id else {}),
            )
            .all()
        )
        serializer = TagsSerializer(tags, many=True)
        return Response(serializer.data)


@extend_schema(
    description="get catalog menu",
    tags=["catalog"],
    responses={200: CategoriesSerializer, 400: ErrorSerializer},
)
class CategoriesAPIView(APIView):
    def get(self, request, *args):
        categories = Category.objects.filter(parent__isnull=True).all()
        serializer = CategoriesSerializer(categories, many=True)
        return Response(serializer.data)


@extend_schema(
    description="get banner items",
    tags=["catalog"],
    request=BannerSerializer,
    responses={200: BannerSerializer, 400: {"error": "Bad Request"}},
)
class BannersAPIView(APIView):
    def get(self, request, *args):
        # Группируем по категориям и возвращаем мин. цену
        min_prices = Product.objects.values("category_id").annotate(
            min_price=Min("price")
        )
        # выбираем товары, где price равен минимальной цене в их подкатегории.
        products = (
            Product.objects.filter(
                archived=False,
                category__isnull=False,
                price__in=[item["min_price"] for item in min_prices],
            )
            .select_related("category")
            .order_by("price")
            .distinct()[:3]
        )

        serializer = BannerSerializer(products, many=True)

        return Response(serializer.data)


@extend_schema(
    description="get catalog popular items",
    tags=["catalog"],
    request=ProductsHomePageSerializer,
    responses={200: ProductsHomePageSerializer, 400: {"error": "Bad Request"}},
)
class ProductsPopularAPIView(APIView):
    """
    Получить топ продуктов
    """

    def get(self, request, *args):
        result = products_home_page(stop=8, sort_index=10)
        return Response(result)


@extend_schema(
    description="get catalog popular items",
    tags=["catalog"],
    request=ProductsHomePageSerializer,
    responses={200: ProductsHomePageSerializer, 400: {"error": "Bad Request"}},
)
class ProductsLimitedAPIView(APIView):
    """
    Получить limited edition продуктов
    """

    def get(self, request, *args):
        result = products_home_page(stop=16, limit_edition=True)
        return Response(result)


@extend_schema(
    description="get sales items",
    tags=["catalog"],
    request=SalesSerializer,
    responses={200: SalesSerializer, 400: {"error": "Bad Request"}},
)
class ProductsSalesAPIView(APIView):
    """
    Получить распродажу продуктов
    """

    def get(self, request, *args):
        now = timezone.now()
        products = (
            Product.objects.filter(
                # Продукт на распродаже СЕЙЧАС
                Q(salePrice__isnull=False)
                & Q(dateFrom__lte=now)  # Начало <= сейчас
                & Q(dateTo__gte=now),
                archived=False,  # Конец >= сейчас
            )
            .select_related("category")
            .prefetch_related("image_set")
            .defer("description", "count", "freeDelivery", "date", "tags")
        )

        serializer = SalesSerializer(products, many=True)

        # вычисление параметров пагинации
        currentPage = int(request.query_params.get("currentPage", 1))
        result = list(serializer.data)
        numbers = len(result)
        limit = 20
        lastPage = numbers // limit

        if numbers % limit:
            lastPage += 1

        start = (currentPage - 1) * limit
        stop = start + limit

        result = serializer.data
        return Response(
            {
                "items": result[start:stop],
                "currentPage": currentPage,
                "lastPage": lastPage,
            }
        )


@extend_schema(
    description="get product",
    tags=["product"],
    request=ProductSerializer,
    responses={200: ProductSerializer, 400: {"error": "Bad Request"}},
)
class ProductAPIView(APIView):
    """
    Получить продукт
    """

    def get(self, request, id=None, format=None):
        product = get_object_or_404(
            Product.objects.defer("created_by", "archived")
            .prefetch_related("tags", "review_set", "image_set", "specification_set")
            .select_related("category")
            .annotate(rating=Avg("review__rate")),
            pk=id,
        )
        serializer = ProductSerializer(product)
        return Response(serializer.data)


@extend_schema(
    description="post product review",
    tags=["product"],
    request=ReviewsSerializer,
    responses={200: ReviewsSerializer, 400: {"error": "Bad Request"}},
)
class ProductReviewAPIView(APIView):
    """
    Отправить отзыв на продукт
    """

    def post(self, request, id=None, format=None):
        # ожидаем, что POST направлен на добавление отзыва к конкретному продукту
        if id is None:
            return Response(
                {"detail": "Missing product id in URL for posting a review."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        product = get_object_or_404(
            Product.objects.prefetch_related("review_set"), pk=id
        )

        serializer = ReviewsSerializer(data=request.data)
        if serializer.is_valid():
            # создание отзыва и привязка к продукту
            Review.objects.create(
                product=product,
                author=serializer.validated_data.get("author"),
                email=serializer.validated_data.get("email"),
                text=serializer.validated_data.get("text"),
                rate=serializer.validated_data.get("rate"),
            )
            # вернуть обновленный набор отзывов или сам созданный объект
            # сериализованный новый отзыв
            new_review = product.review_set.order_by("-date").first()
            return Response(
                ReviewsSerializer(new_review).data, status=status.HTTP_201_CREATED
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BasketAPIView(APIView):
    """
    Получить/изменить/удалить корзину продуктов
    """

    @extend_schema(
        description="Get items in basket",
        tags=["basket"],
        request=BasketItemSerializer,
        responses={200: BasketItemSerializer, 400: {"error": "Bad Request"}},
    )
    def get(self, request, *args):
        if request.user.is_authenticated:
            basket = user_basket(request)
            if basket:
                items = basket.items.select_related("product").all()
                serializer = BasketItemSerializer(items, many=True)
                result = serializer.data
            else:
                result = {}
            return Response(result)

        else:
            basket = anon_basket(request)
            items_data = []
            for product_id, count in basket.items():
                try:
                    product = Product.objects.prefetch_related("image_set").get(
                        id=product_id
                    )
                    item_data = {
                        "id": product.id,
                        "title": product.title,
                        "price": product.get_current_price(),
                        "images": ImagesSerializer(product.image_set, many=True).data,
                        "count": count,
                    }
                    items_data.append(item_data)
                except Product.DoesNotExist:
                    continue

            return Response(items_data)

    @extend_schema(
        description="Add item to basket",
        tags=["basket"],
        request=AddDeleteBasketSerializer,
        responses={200: SuccessSerializer, 400: ErrorSerializer},
    )
    def post(self, request, *args):
        """
        Метод для добавления продуктов в корзину
        """
        data = request.data
        result = change_basket(request, data)
        return Response({"message": result["message"]}, result["status"])

    @extend_schema(
        description="Remove item from basket",
        tags=["basket"],
        request=AddDeleteBasketSerializer,
        responses={200: SuccessSerializer, 400: ErrorSerializer},
    )
    def delete(self, request, *args):
        """
        Метод для удаления продуктов из корзины по одному, или всей позиции сразу
        """
        data = request.data
        result = change_basket(request, data, delete=True)
        return Response({"message": result["message"]}, result["status"])
