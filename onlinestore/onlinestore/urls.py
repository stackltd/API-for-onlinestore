from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)

from .api import APIRootView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("frontend.urls")),
    path("api/", include("catalog.urls")),
    path("api/", include("accounts.urls")),
    path("api/", include("orders.urls")),
    path("api/", APIRootView.as_view(), name="api-root"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    path("api-auth/", include("rest_framework.urls")),
]


if settings.DEBUG:
    for param in (settings.MEDIA_URL, settings.MEDIA_ROOT), (
        settings.STATIC_URL,
        settings.STATIC_ROOT,
    ):
        urlpatterns.extend(static(param[0], document_root=param[1]))
