from django.contrib.auth import authenticate, login, get_user_model
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.response import Response

from onlinestore.dao import DAO
from .serializers import ProfileSerializer
from .models import Profile


class AuthService:

    @classmethod
    def sign_in(cls, request):
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

    @classmethod
    def sign_up(cls, request):
        username = request.data.get("username")
        firstname = request.data.get("name", "")
        password = request.data.get("password")
        if not username or not password:
            return Response(
                {"error": "Username and password required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        User = get_user_model()
        user_exists = DAO.search_object_by_fields(User, filter=dict(username=username))
        if user_exists.exists():
            return Response(
                {"error": f"Username '{username}' already exists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = DAO.user_create(
            User, dict(username=username, password=password, first_name=firstname)
        )
        login(request, user)
        return Response(
            {"description": "successful operation"}, status=status.HTTP_200_OK
        )

    @classmethod
    def get_profile(cls, request):
        profile, _ = DAO.create_or_get(Profile, dict(user=request.user))
        serializer = ProfileSerializer(profile)
        result = serializer.data
        return Response(result)

    @classmethod
    def change_profile(cls, request):
        data = request.data
        if data.get("avatar"):
            data.pop("avatar")
        profile = DAO.get_object(Profile, dict(user=request.user))
        updatable = ["fullName", "email", "phone"]
        for field in updatable:
            if field in data:
                value = data[field]
                setattr(profile, field, value)
        update_fields = [f for f in updatable if f in data]
        profile.save(update_fields=update_fields)
        return Response(data)

    @classmethod
    def set_avatar(cls, request):
        data = request.data
        avatar = data.get("avatar")
        if avatar:
            profile = DAO.get_object(Profile, dict(user=request.user))
            profile.avatar = avatar
            profile.save()
            return Response({"result": "successful operation"})
        return Response({"error": "Bad Request"})

    @classmethod
    def change_password(cls, request):
        try:
            data = request.data
            passwordCurrent = data["passwordCurrent"]
            password = data["password"]
            passwordReply = data["passwordReply"]
            user = request.user
            if not user.check_password(passwordCurrent):
                return Response(
                    {"error": "Enter correctly current password"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            if password == passwordReply:
                user.set_password(password)
                user.save()
                return Response({"result": "successful operation"})

            return Response(
                {"error": "Enter correctly passwords"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except ValidationError as e:
            return Response(
                {"error": "Your new password is not correct!"},
                status=status.HTTP_400_BAD_REQUEST,
            )
