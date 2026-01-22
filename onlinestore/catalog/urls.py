from django.urls import path

from .api import (
    CatalogAPIView,
    TagsAPIView,
    CategoriesAPIView,
    BannersAPIView,
    ProductsPopularAPIView,
    ProductsLimitedAPIView,
    ProductsSalesAPIView,
    ProductAPIView,
    ProductReviewAPIView,
    BasketAPIView,
)

app_name = "catalog"

urlpatterns = [
    path("catalog/", CatalogAPIView.as_view(), name="catalog"),
    path("tags/", TagsAPIView.as_view(), name="tags"),
    path("categories/", CategoriesAPIView.as_view(), name="categories"),
    path("banners/", BannersAPIView.as_view(), name="banners"),
    path(
        "products/popular/", ProductsPopularAPIView.as_view(), name="products_popular"
    ),
    path(
        "products/limited/", ProductsLimitedAPIView.as_view(), name="products_limited"
    ),
    path("product/<int:id>/", ProductAPIView.as_view(), name="product_details"),
    path(
        "product/<int:id>/reviews/",
        ProductReviewAPIView.as_view(),
        name="product-review",
    ),
    path("sales/", ProductsSalesAPIView.as_view(), name="sales"),
    path("basket/", BasketAPIView.as_view(), name="basket"),
]
