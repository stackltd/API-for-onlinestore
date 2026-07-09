from django.db.models import Count, Avg, Min, Q
from rest_framework import status
from rest_framework.response import Response
from django.utils import timezone


from .models import Product, Tag, Category, Review, Basket, BasketItem
from onlinestore.dao import DAO
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
    ImagesSerializer,
)


class CatalogService:
    @classmethod
    def get_catalog(cls, request):
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

        name = _name or __name

        tag_ids = []
        tag_id = filter.get("tags[]", "")
        if tag_id:
            tag_ids.append(tag_id)

        # вычисление списка родительских, или дочерних категорий для product
        category_id = filter["category"]
        cat_sub_ids = []
        if category_id:
            # При parent_id=None получаем родительские категории
            # parent_id = Category.objects.filter(id=category_id).first().parent_id
            parent_id = DAO.search_object_by_fields(
                model=Category, filter={"id": category_id}, ext_method="first"
            ).parent_id
            print(parent_id)
            cat_sub_ids = [
                obj.pk
                for obj in DAO.search_object_by_fields(
                    model=Category,
                    filter={
                        **({"id": category_id} if parent_id else {}),
                        **({"parent_id": category_id} if not parent_id else {}),
                    },
                    ext_method="all",
                )
            ]
        # получаем продукты со связанными таблицами и агрегированными данными, производим сортировку и фильтрацию

        products = DAO.search_object_by_fields(
            model=Product,
            defer=("created_by", "archived", "fullDescription", "sortIndex"),
            prefetch_related=("tags", "review_set", "image_set"),
            select_related=("category",),
            annotate={"reviews": Count("review"), "rating": Avg("review__rate")},
            filter={
                "archived": False,
                "price__gte": filter["minPrice"],
                "price__lte": filter["maxPrice"],
                **({"category__id__in": cat_sub_ids} if cat_sub_ids else {}),
                **({"tags__id__in": tag_ids} if tag_ids else {}),
                **({"count__gt": 0} if filter["available"] == "true" else {}),
                **({"freeDelivery": True} if filter["Delivery"] == "true" else {}),
                **({"title__iregex": name} if name else {}),
            },
            order_by=(
                f"-{order_param}" if filter["sortType"] == "inc" else f"{order_param}"
            ),
        ).all()

        serializer = CatalogSerializer(products, many=True)

        # вычисление параметров пагинации
        currentPage = int(filter.get("currentPage", 1))
        result = list(serializer.data)
        numbers = len(result)
        start, stop, lastPage = CatalogService._pagination(
            numbers=numbers, currentPage=currentPage, limit=8
        )

        return Response(
            {
                "items": result[start:stop],
                "currentPage": currentPage,
                "lastPage": lastPage,
            }
        )

    @classmethod
    def get_tags(cls, request):
        query = dict(request.query_params)
        category_id = query.get("category", [None])[0]
        tags = DAO.search_object_by_fields(
            model=Tag,
            select_related=("category",),
            filter={
                **({"category__id__in": [category_id]} if category_id else {}),
            },
            ext_method="all",
        )
        serializer = TagsSerializer(tags, many=True)
        return Response(serializer.data)

    @classmethod
    def get_categories(cls):
        categories = DAO.search_object_by_fields(
            model=Category, filter=dict(parent__isnull=True), ext_method="all"
        )
        serializer = CategoriesSerializer(categories, many=True)
        return Response(serializer.data)

    @classmethod
    def get_banners(cls):
        # Группируем по категориям и возвращаем мин. цену
        min_prices = DAO.search_object_by_fields(
            model=Product, values=("category_id",), annotate={"min_price": Min("price")}
        )
        products = DAO.search_object_by_fields(
            model=Product,
            filter=dict(
                archived=False,
                category__isnull=False,
                price__in=[item["min_price"] for item in min_prices],
            ),
            select_related=("category",),
            order_by="price",
            ext_method="distinct",
        )[:3]
        serializer = BannerSerializer(products, many=True)

        return Response(serializer.data)

    @classmethod
    def get_products_home_page(cls, stop=-1, sort_index=None, limit_edition=False):
        """Возвращает объекты products, отфильтрованный по одному из заданных параметров sort_index, или limit_edition"""
        products = DAO.search_object_by_fields(
            model=Product,
            defer=(
                "created_by",
                "archived",
                "fullDescription",
                "description",
                "count",
                "freeDelivery",
                "date",
                "tags",
                "category",
            ),
            prefetch_related=("image_set",),
            annotate={"rating": Avg("review__rate")},
            filter={
                **({"sortIndex__lte": sort_index} if sort_index else {}),
                **({"limitedEdition": True} if limit_edition else {}),
            },
            ext_method="distinct",
        )[:stop]

        serializer = ProductsHomePageSerializer(products, many=True)
        result = serializer.data

        return Response(result)

    @classmethod
    def get_sales(cls, request):
        now = timezone.now()
        products = DAO.search_object_by_fields(
            model=Product,
            filter=dict(  # Продукт на распродаже СЕЙЧАС
                salePrice__isnull=False,
                dateFrom__lte=now,  # Начало <= сейчас
                dateTo__gte=now,  # Конец >= сейчас)
                archived=False,
            ),
            select_related=("category",),
            prefetch_related=("image_set",),
            defer=("description", "count", "freeDelivery", "date", "tags"),
        )

        serializer = SalesSerializer(products, many=True)

        # вычисление параметров пагинации
        currentPage = int(request.query_params.get("currentPage", 1))

        result = list(serializer.data)
        numbers = len(result)

        start, stop, lastPage = CatalogService._pagination(
            numbers=numbers, currentPage=currentPage, limit=20
        )

        return Response(
            {
                "items": result[start:stop],
                "currentPage": currentPage,
                "lastPage": lastPage,
            }
        )

    @classmethod
    def get_product(cls, id):
        product = DAO.search_object_by_fields(
            model=Product,
            defer=("created_by", "archived"),
            prefetch_related=("tags", "review_set", "image_set", "specification_set"),
            select_related=("category",),
            annotate=(dict(rating=Avg("review__rate"))),
            get_object_or_404_params={"pk": id},
        )

        serializer = ProductSerializer(product)
        return Response(serializer.data)

    @classmethod
    def post_product_review(cls, request, id):
        # ожидаем, что POST направлен на добавление отзыва к конкретному продукту
        if id is None:
            return Response(
                {"detail": "Missing product id in URL for posting a review."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        product = DAO.search_object_by_fields(
            model=Product,
            prefetch_related=("review_set",),
            get_object_or_404_params={"pk": id},
        )

        serializer = ReviewsSerializer(data=request.data)
        if serializer.is_valid():
            # создание отзыва и привязка к продукту
            DAO.create_or_get(
                Review,
                dict(
                    product=product,
                    author=serializer.validated_data.get("author"),
                    email=serializer.validated_data.get("email"),
                    text=serializer.validated_data.get("text"),
                    rate=serializer.validated_data.get("rate"),
                ),
            )
            new_review = DAO.search_object_by_fields(
                _object=product.review_set, order_by="-date", ext_method="first"
            )
            return Response(
                ReviewsSerializer(new_review).data, status=status.HTTP_201_CREATED
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @classmethod
    def get_basket(cls, request):
        if request.user.is_authenticated:
            basket = cls._user_basket(request)
            if basket:
                items = DAO.search_object_by_fields(
                    _object=basket.items, select_related=("product",), ext_method="all"
                )
                serializer = BasketItemSerializer(items, many=True)
                result = serializer.data
            else:
                result = {}
            return Response(result)

        else:
            basket = cls._anon_basket(request)
            items_data = []
            for product_id, count in basket.items():
                try:
                    product = DAO.search_object_by_fields(
                        model=Product,
                        prefetch_related=("image_set",),
                        get={"id": product_id},
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

    @classmethod
    def add_basket(cls, request):
        data = request.data
        result = cls._change_basket(request, data)
        return Response({"message": result["message"]}, result["status"])

    @classmethod
    def delete_basket(cls, request):
        data = request.data
        result = cls._change_basket(request, data, delete=True)
        return Response({"message": result["message"]}, result["status"])

    @staticmethod
    def _pagination(numbers, currentPage, limit):
        lastPage = numbers // limit

        if numbers % limit:
            lastPage += 1

        start = (currentPage - 1) * limit
        stop = start + limit

        return start, stop, lastPage

    @classmethod
    def _user_basket(cls, request):
        """
        Ссоздание корзины зарегистрированного пользователя и слияние её с корзиной анонима, если она не пустая
        """
        basket, created = DAO.create_or_get(
            model=Basket,
            data_dict=dict(user=request.user, defaults={"user": request.user}),
        )  # Только для user
        # Находим анонимную корзину
        basket_anon = cls._anon_basket(request)
        if basket_anon:
            # Переносим товары в корзину пользователя
            basket_user, _ = DAO.create_or_get(
                model=Basket, data_dict={"user": request.user}
            )
            items = [
                BasketItem(basket=basket_user, product_id=product_id, count=count)
                for product_id, count in basket_anon.items()
            ]
            BasketItem.objects.bulk_create(items)
            if "basket" in request.session:
                del request.session["basket"]

        return basket

    @staticmethod
    def _anon_basket(request) -> dict:
        """
        Получение из сессии корзины анонима
        """
        session = request.session
        if not session.session_key:
            session.update({"basket": {}})
        basket = session.get("basket", {})
        return basket

    @classmethod
    def _change_basket(cls, request, data, delete=False):
        """
        Создание/изменение корзины
        """
        id = str(data["id"])
        count = data.get("count", 1)
        if request.user.is_authenticated:
            # для корзины авторизованного пользователя (из бд)
            basket = cls._user_basket(request)
            if delete:
                item = BasketItem.objects.filter(
                    basket=basket, product_id=data["id"]
                ).first()
                if not item:
                    return {"status": 400, "message": "Item not in basket"}

                if item.count > count:
                    item.count -= count
                    item.save()
                else:
                    item.delete()
            else:
                product = Product.objects.filter(id=id).first()
                if not product:
                    return {"message": "Product not found", "status": 400}
                item, created = BasketItem.objects.get_or_create(
                    basket=basket, product=product, defaults={"count": count}
                )
                if not created:
                    item.count += data.get("count", 1)
                    item.save()
        else:
            # для корзины анонимного пользователя (из сессии)
            session = request.session
            basket = cls._anon_basket(request)
            count_in_basket = basket.get(id, 0)

            if delete:
                if count_in_basket > count:
                    count_in_basket -= count
                else:
                    basket.pop(id)
                    session["basket"] = basket
                    return {"message": "successful", "status": 200}
            else:
                count_in_basket += count

            basket[id] = count_in_basket
            session["basket"] = basket

        return {"message": "successful", "status": 200}
