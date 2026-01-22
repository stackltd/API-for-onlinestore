from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView


@extend_schema(exclude=True)
class APIRootView(APIView):
    def get(self, request):
        return Response(
            {
                "catalog": {
                    "catalog": reverse("catalog:catalog", request=request),
                    "tags": reverse("catalog:tags", request=request),
                    "categories": reverse("catalog:categories", request=request),
                    "banners": reverse("catalog:banners", request=request),
                    "products_popular": reverse(
                        "catalog:products_popular", request=request
                    ),
                    "products_limited": reverse(
                        "catalog:products_limited", request=request
                    ),
                    "product": reverse(
                        "catalog:product_details", kwargs={"id": 0}, request=request
                    ),
                    "sales": reverse("catalog:sales", request=request),
                    "basket": reverse("catalog:basket", request=request),
                },
                "accounts": {
                    "sign-in": reverse("accounts:sign-in", request=request),
                    "sign-up": reverse("accounts:sign-up", request=request),
                    "sign-out": reverse("accounts:sign-out", request=request),
                    "profile": reverse("accounts:profile", request=request),
                    "profile-avatar": reverse(
                        "accounts:profile-avatar", request=request
                    ),
                    "profile-password": reverse(
                        "accounts:profile-password", request=request
                    ),
                },
            }
        )
