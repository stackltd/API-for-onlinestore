from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiResponse

from .serializers import (
    SignIpSerializer,
    SignUpSerializer,
    ProfileSerializer,
    UploadSerializer,
    ChangePasswordSerializer,
)


sign_in_schema = dict(
    description="sign-in",
    tags=["auth"],
    request=SignIpSerializer,
    responses={200: SignIpSerializer, 400: {"error": "Bad Request"}},
)


sign_out_schema = dict(
    tags=["auth"], request=None, responses={200: OpenApiTypes.OBJECT}
)

sign_up_schema = dict(
    tags=["auth"],
    request=SignUpSerializer,
    responses={200: SignUpSerializer, 400: {"error": "Bad Request"}},
)

get_profile_schema = dict(
    description="Get user profile",
    tags=["profile"],
    request=ProfileSerializer,
    responses={200: ProfileSerializer, 400: {"error": "Bad Request"}},
)

change_profile_schema = dict(
    description="update user info",
    tags=["profile"],
    request=ProfileSerializer,
    responses={200: ProfileSerializer, 400: {"error": "Bad Request"}},
)

set_avatar_schema = dict(
    description="update user avatar",
    tags=["profile"],
    request=UploadSerializer,
    responses={
        200: OpenApiResponse(
            description="Successful operation",
        ),
        400: OpenApiResponse(
            description="Bad Request",
        ),
    },
)

change_password_schema = dict(
    description="update user password",
    tags=["profile"],
    request=ChangePasswordSerializer,
    responses={
        200: {"result": "successful operation"},
        400: {"error": "operation was failed"},
    },
)
