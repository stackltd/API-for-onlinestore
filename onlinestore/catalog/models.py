import os

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import (
    CharField,
    TextField,
    DecimalField,
    SmallIntegerField,
    DateTimeField,
    BooleanField,
    ForeignKey,
    ManyToManyField,
    ImageField,
    PROTECT,
    CASCADE,
    Model,
    EmailField,
    PositiveIntegerField,
)

from django.contrib.auth.models import User
from django.utils import timezone


curr_dir = os.getcwd()


def clear_uploads(path, inst):
    """
    Очистка папок с продуктами и профилей пользователей от неиспользуемых картинок
    """
    all_path = os.path.join(curr_dir, path)
    image = Image.objects.filter(id=inst.pk).first()
    if image:
        if os.path.exists(all_path):
            os.chdir(all_path)
            name = str(image.src).split("/")[-1]
            if os.path.exists(name):
                os.remove(name)
        os.chdir(curr_dir)


def clear_uploads_category(inst, obj, path):
    """
    Очистка папок каталогов и подкаталогов от неиспользуемых картинок
    """
    result = obj.objects.filter(id=inst.pk)
    # удаление старого файла при замене картинки
    if result:
        image_path = result.first().image.path
        os.chdir(os.path.join(curr_dir, path))
        image_name = image_path.split("/")[-1]
        if os.path.exists(image_name):
            os.remove(image_name)

    # удаление файлов, которым нет соответствия в базе данных
    parent_id = result.first().parent_id
    categories = obj.objects.filter(
        **({"parent_id": parent_id} if parent_id else {}),
        **({"parent__isnull": True} if not parent_id else {}),
    ).all()
    names = [str(category.image).split("/")[-1] for category in categories]
    for file in os.listdir():
        if file not in names:
            os.remove(file)

    os.chdir(curr_dir)


def prod_images_dir_path(inst: "Image", filename: str) -> str:
    path = f"product/{inst.product.pk}/{filename}"
    clear_uploads(path=f"uploads/product/{inst.product.pk}", inst=inst)
    return path


def category_image_path(inst, filename):
    path = f"category/{inst.parent.pk}" if inst.parent else "category/0"
    clear_uploads_category(inst=inst, obj=Category, path=f"uploads/{path}")
    return f"{path}/{filename}"


class Category(Model):
    title = CharField("Название", max_length=200)
    image = ImageField(
        "Изображение", upload_to=category_image_path, blank=True, null=True
    )
    parent = ForeignKey(
        "self",
        on_delete=PROTECT,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="Родительская категория",
    )

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        if self.parent:
            return f"{self.parent.title} → {self.title}"
        return self.title

    @property
    def is_root(self):
        return self.parent is None


class Product(Model):
    """
    Product(id, title, description, fullDescription, price, count, freeDelivery, date, archived)

    Модель Product представляет товар, который можно продавать в интернет-магазине

    Заказы: :model: `catalog.order`
    """

    title = CharField(max_length=100, db_index=True)
    description = TextField(null=False, blank=True, db_index=True)
    fullDescription = TextField(null=False, blank=True)
    price = DecimalField(
        default=0, decimal_places=2, max_digits=12, validators=[MinValueValidator(0)]
    )
    count = SmallIntegerField(default=0, validators=[MinValueValidator(0)])
    freeDelivery = BooleanField(default=False)
    sortIndex = SmallIntegerField(
        default=100, validators=[MinValueValidator(0), MaxValueValidator(999)]
    )
    limitedEdition = BooleanField(default=False)
    salePrice = DecimalField(
        default=0, decimal_places=2, max_digits=12, validators=[MinValueValidator(0)]
    )
    dateFrom = DateTimeField(null=True, blank=True)
    dateTo = DateTimeField(null=True, blank=True)
    date = DateTimeField(auto_now_add=True)
    created_by = ForeignKey(User, on_delete=PROTECT, editable=False)
    archived = BooleanField(default=False)
    tags = ManyToManyField("Tag", related_name="products")
    category = ForeignKey(
        Category,
        on_delete=PROTECT,
        related_name="products",
        verbose_name="Категория",
        help_text="Только дочерние категории",
        null=True,
        blank=True,
    )

    def __str__(self):
        return self.title

    def get_current_price(self):
        now = timezone.now()
        if self.dateFrom and self.dateTo:
            if self.dateFrom <= now and self.dateTo >= now:
                return self.salePrice
        return self.price


class Image(Model):
    product = ForeignKey(Product, on_delete=PROTECT)
    src = ImageField(upload_to=prod_images_dir_path)
    alt = CharField(max_length=200, null=False, blank=True)


class Tag(Model):
    name = CharField(max_length=20)
    category = ForeignKey("Category", on_delete=PROTECT, null=True, blank=True)

    def __str__(self):
        return self.name


class Review(Model):
    product = ForeignKey(Product, on_delete=PROTECT)
    author = CharField(max_length=100)
    email = EmailField(null=False, blank=True)
    text = TextField(null=False, blank=False)
    rate = SmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    date = DateTimeField(auto_now_add=True)


class Specification(Model):
    product = ForeignKey(Product, on_delete=PROTECT)
    name = CharField(max_length=100, db_index=True)
    value = CharField(max_length=100, db_index=True)

    def __str__(self):
        return f"{self.name}: {self.value}"


class Basket(Model):
    user = ForeignKey(User, on_delete=CASCADE)


class BasketItem(Model):
    basket = ForeignKey(Basket, on_delete=CASCADE, related_name="items")
    product = ForeignKey(Product, on_delete=CASCADE)
    count = PositiveIntegerField(default=1)

    class Meta:
        unique_together = ("basket", "product")
