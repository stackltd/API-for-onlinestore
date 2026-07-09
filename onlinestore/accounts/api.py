from django.http import HttpRequest
from django.contrib.auth import logout
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated, AllowAny

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .services import AuthService
from .swagger_schemas import (
    sign_in_schema,
    sign_out_schema,
    sign_up_schema,
    get_profile_schema,
    change_profile_schema,
    set_avatar_schema,
    change_password_schema,
)


@extend_schema(**sign_in_schema)
class SignInView(APIView):
    def post(self, request: HttpRequest):
        """Вход в систему"""
        result = AuthService.sign_in(request)
        return result


class SignOutView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(**sign_out_schema)
    def post(self, request):
        """Выход из системы"""
        logout(request)
        return Response(
            {"description": "successful operation"}, status=status.HTTP_200_OK
        )


@extend_schema(**sign_up_schema)
class SignUpView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """Регистрация нового пользователя"""
        result = AuthService.sign_up(request)
        return result


class ProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(**get_profile_schema)
    def get(self, request, *args):
        """Получить профиль пользователя"""
        return AuthService.get_profile(request)

    @extend_schema(**change_profile_schema)
    def post(self, request, *args):
        """Изменить профиль пользователя"""
        return AuthService.change_profile(request)


@extend_schema(**set_avatar_schema)
class ProfileAvatarAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args):
        """Установить аватар пользователя"""
        return AuthService.set_avatar(request)


@extend_schema(**change_password_schema)
class ProfilePasswordAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args):
        """Изменить пароль"""
        return AuthService.change_password(request)
