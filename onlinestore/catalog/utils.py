from django.db.models import Avg

from .models import Product, Basket, BasketItem
from .serializers import ProductsHomePageSerializer


def products_home_page(stop=-1, sort_index=None, limit_edition=False):
    """
    Метод передает объекты products, отфильтрованный по одному из заданных параметров sort_index, или limit_edition
    """
    products = (
        Product.objects.defer("created_by", "archived", "fullDescription")
        .defer("description", "count", "freeDelivery", "date", "tags", "category")
        .prefetch_related("image_set")
        .annotate(
            rating=Avg("review__rate"),
        )
        .filter(
            **({"sortIndex__lte": sort_index} if sort_index else {}),
            **({"limitedEdition": True} if limit_edition else {}),
        )
    ).distinct()[:stop]

    serializer = ProductsHomePageSerializer(products, many=True)
    result = serializer.data

    return result


def user_basket(request):
    """
    Ссоздание корзины зарегистрированного пользователя и слияние её с корзиной анонима, если она не пустая
    """
    basket, created = Basket.objects.get_or_create(
        user=request.user, defaults={"user": request.user}  # Только для user
    )

    # Находим анонимную корзину
    basket_anon = anon_basket(request)
    if basket_anon:
        # Переносим товары в корзину пользователя
        user_basket, _ = Basket.objects.get_or_create(user=request.user)
        user_basket.items.all().delete()

        items = [
            BasketItem(basket=user_basket, product_id=product_id, count=count)
            for product_id, count in basket_anon.items()
        ]
        BasketItem.objects.bulk_create(items)
        if "basket" in request.session:
            del request.session["basket"]

    return basket


def anon_basket(request) -> dict:
    """
    Получение из сессии корзины анонима
    """
    session = request.session
    if not session.session_key:
        session.update({"basket": {}})
    basket = session.get("basket", {})
    return basket


def change_basket(request, data, delete=False):
    """
    Создание/изменение корзины
    """
    id = str(data["id"])
    count = data.get("count", 1)
    if request.user.is_authenticated:
        # для корзины авторизованного пользователя (из бд)
        basket = user_basket(request)
        if delete:
            item = BasketItem.objects.filter(
                basket=basket, product_id=data["id"]
            ).first()
            if not item:
                return {"status": 400, "message": "Item not in basket"}

            if item.count > count:
                item.count -= count
                item.save()
            else:
                item.delete()
        else:
            product = Product.objects.filter(id=id).first()
            if not product:
                return {"message": "Product not found", "status": 400}
            item, created = BasketItem.objects.get_or_create(
                basket=basket, product=product, defaults={"count": count}
            )
            if not created:
                item.count += data.get("count", 1)
                item.save()
    else:
        # для корзины анонимного пользователя (из сессии)
        session = request.session
        basket = anon_basket(request)
        count_in_basket = basket.get(id, 0)

        if delete:
            if count_in_basket > count:
                count_in_basket -= count
            else:
                basket.pop(id)
                session["basket"] = basket
                return {"message": "successful", "status": 200}
        else:
            count_in_basket += count

        basket[id] = count_in_basket
        session["basket"] = basket

    return {"message": "successful", "status": 200}
