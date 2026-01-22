from django.core.exceptions import ValidationError
from django.http import HttpRequest
from django.contrib.auth import authenticate, login, logout, get_user_model
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework.permissions import IsAuthenticated, AllowAny

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import (
    SignIpSerializer,
    SignUpSerializer,
    ProfileSerializer,
    UploadSerializer,
    ChangePasswordSerializer,
)
from .models import Profile


@extend_schema(
    description="sign-in",
    tags=["auth"],
    request=SignIpSerializer,
    responses={200: SignIpSerializer, 400: {"error": "Bad Request"}},
)
class SignInView(APIView):

    def post(self, request: HttpRequest):
        data_in = dict(request.data)
        username = data_in.get("username")
        password = data_in.get("password")
        if not username or not password:
            return Response(
                {"error": "Login and password required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response(
                {"description": "successful operation"}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"description": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class SignOutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["auth"], request=None, responses={200: OpenApiTypes.OBJECT})
    def post(self, request):
        logout(request)
        return Response(
            {"description": "successful operation"}, status=status.HTTP_200_OK
        )


@extend_schema(
    tags=["auth"],
    request=SignUpSerializer,
    responses={200: SignUpSerializer, 400: {"error": "Bad Request"}},
)
class SignUpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        User = get_user_model()
        username = request.data.get("username")
        firstname = request.data.get("name", "")
        password = request.data.get("password")
        if not username or not password:
            return Response(
                {"error": "Username and password required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(username=username).exists():
            return Response(
                {"error": "Username already exists"}, status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.create_user(
            username=username, password=password, first_name=firstname
        )
        user.save()
        login(request, user)

        return Response(
            {"description": "successful operation"}, status=status.HTTP_200_OK
        )


class ProfileAPIView(APIView):
    """
    Получить профиль пользователя
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        description="Get user profile",
        tags=["profile"],
        request=ProfileSerializer,
        responses={200: ProfileSerializer, 400: {"error": "Bad Request"}},
    )
    def get(self, request, *args):
        profile, _ = Profile.objects.get_or_create(user=request.user)
        serializer = ProfileSerializer(profile)
        result = serializer.data
        return Response(result)

    @extend_schema(
        description="update user info",
        tags=["profile"],
        request=ProfileSerializer,
        responses={200: ProfileSerializer, 400: {"error": "Bad Request"}},
    )
    def post(self, request, *args):
        data = request.data
        if data.get("avatar"):
            data.pop("avatar")
        profile = Profile.objects.get(user=request.user)
        updatable = ["fullName", "email", "phone"]
        for field in updatable:
            if field in data:
                value = data[field]
                setattr(profile, field, value)
        profile.save(update_fields=[f for f in updatable if f in data])
        return Response(data)


@extend_schema(
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
class ProfileAvatarAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args):
        data = request.data
        avatar = data.get("avatar")
        if avatar:
            profile = Profile.objects.get(user=request.user)
            profile.avatar = avatar
            profile.save()
            return Response({"result": "successful operation"})
        return Response({"error": "Bad Request"})


@extend_schema(
    description="update user password",
    tags=["profile"],
    request=ChangePasswordSerializer,
    responses={
        200: {"result": "successful operation"},
        400: {"error": "operation was failed"},
    },
)
class ProfilePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args):
        data = request.data
        passwordCurrent = data["passwordCurrent"]
        password = data["password"]
        passwordReply = data["passwordReply"]
        user = request.user
        if not user.check_password(passwordCurrent):
            return Response({"error": "Enter correctly current password"})
        if password == passwordReply:
            try:
                # validate_password(password, user=user)
                user.set_password(password)
                user.save()
                return Response({"result": "successful operation"})
            except ValidationError as e:
                return Response({"error": "Your new password is not correct!"})
        return Response({"error": "Enter correctly passwords"})
