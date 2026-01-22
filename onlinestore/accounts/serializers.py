from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import (
    Serializer,
    CharField,
    ModelSerializer,
    FileField,
    ImageField,
)

from .models import Profile


class SignIpSerializer(Serializer):
    username = CharField(default="Your login")
    password = CharField(write_only=True, default="Your password")


class SignUpSerializer(Serializer):
    username = CharField(default="Your login")
    firstname = CharField(required=False, default="Your name")
    password = CharField(write_only=True, default="Your password")


class ProfileSerializer(ModelSerializer):
    avatar = SerializerMethodField()

    class Meta:
        model = Profile
        fields = (
            "user",
            "fullName",
            "email",
            "phone",
            "avatar",
        )

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_avatar(self, obj):
        if obj.avatar:
            return {"src": obj.avatar.url, "alt": obj.fullName}
        return {}


class UploadSerializer(Serializer):
    file = ImageField()


class ChangePasswordSerializer(Serializer):
    passwordCurrent = CharField(write_only=True, default="Your current password")
    password = CharField(write_only=True, default="Your new password")
    passwordReply = CharField(write_only=True, default="Your new password")
