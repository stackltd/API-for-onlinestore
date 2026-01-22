import os

from django.contrib.auth.models import User
from django.db.models import Model, OneToOneField, TextField, PROTECT, EmailField
from django.db.models import ImageField
from phonenumber_field.modelfields import PhoneNumberField


curr_dir = os.getcwd()


def clear_uploads(curr_dir, path):
    """
    Очистка папок с продуктами и профилей пользователей от неиспользуемых картинок
    """
    all_path = os.path.join(curr_dir, path)
    if os.path.exists(all_path):
        os.chdir(all_path)
        for file in os.listdir():
            os.remove(file)
        os.chdir(curr_dir)


def user_avatar_dir_path(inst: "Profile", filename: str) -> str:
    path = f"profiles/user_{inst.user.pk}/{filename}"
    clear_uploads(curr_dir=curr_dir, path=f"uploads/profiles/user_{inst.user.pk}")
    os.chdir(curr_dir)
    return path


class Profile(Model):
    user = OneToOneField(User, on_delete=PROTECT)
    fullName = TextField(max_length=500, blank=True)
    email = EmailField(null=False, blank=True)
    phone = PhoneNumberField(region=None, null=True, blank=True)
    avatar = ImageField(null=True, blank=True, upload_to=user_avatar_dir_path)

    def __str__(self):
        return f"{self.user, self.fullName, self.email, self.phone}"
