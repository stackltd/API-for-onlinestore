from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView

from .services import CatalogService
from .swagger_schemas import (
    catalog_schema,
    tags_schema,
    categories_schema,
    banners_schema,
    products_popular_schema,
    products_limited_schema,
    sales_schema,
    product_schema,
    product_review_schema,
    get_basket_schema,
    add_basket_schema,
    delete_basket_schema,
)


@extend_schema(**catalog_schema)
class CatalogAPIView(APIView):
    def get(self, request, *args):
        """Каталог продуктов"""
        return CatalogService.get_catalog(request)


@extend_schema(**tags_schema)
class TagsAPIView(APIView):
    def get(self, request, *args):
        """Теги"""
        return CatalogService.get_tags(request)


@extend_schema(**categories_schema)
class CategoriesAPIView(APIView):
    def get(self, request, *args):
        """Категории продуктов"""
        return CatalogService.get_categories()


@extend_schema(**banners_schema)
class BannersAPIView(APIView):
    def get(self, request, *args):
        """Баннеры"""
        return CatalogService.get_banners()


@extend_schema(**products_popular_schema)
class ProductsPopularAPIView(APIView):
    def get(self, request, *args):
        """Топ продуктов"""
        return CatalogService.get_products_home_page(stop=8, sort_index=10)


@extend_schema(**products_limited_schema)
class ProductsLimitedAPIView(APIView):
    def get(self, request, *args):
        """Лимитированные продукты"""
        return CatalogService.get_products_home_page(stop=16, limit_edition=True)


@extend_schema(**sales_schema)
class ProductsSalesAPIView(APIView):
    def get(self, request, *args):
        """Распродажа продуктов"""
        return CatalogService.get_sales(request)


@extend_schema(**product_schema)
class ProductAPIView(APIView):
    def get(self, request, id=None, format=None):
        """Получить продукт"""
        return CatalogService.get_product(id)


@extend_schema(**product_review_schema)
class ProductReviewAPIView(APIView):
    def post(self, request, id=None, format=None):
        """Опубликовать отзыв на продукт"""
        return CatalogService.post_product_review(request, id)


class BasketAPIView(APIView):
    @extend_schema(**get_basket_schema)
    def get(self, request, *args):
        """Получить корзину"""
        return CatalogService.get_basket(request)

    @extend_schema(**add_basket_schema)
    def post(self, request, *args):
        """Добавить продукты в корзину"""
        return CatalogService.add_basket(request)

    @extend_schema(**delete_basket_schema)
    def delete(self, request, *args):
        """удалить продукты из корзины по одному, или всю позицию"""
        return CatalogService.delete_basket(request)
