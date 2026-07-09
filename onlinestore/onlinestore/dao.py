from django.shortcuts import get_object_or_404


class DAO:

    @classmethod
    def search_object_by_fields(
        cls,
        model=None,
        _object=None,
        defer=(),
        values=(),
        prefetch_related=(),
        select_related=(),
        annotate=None,
        filter=None,
        order_by="pk",
        ext_method=None,
        get_object_or_404_params=None,
        get=None,
    ):
        """
        A universal search function in the database using a ready-made object or model
        :param model: use model or _object, else ValueError
        :param _object: use model or _object, else ValueError
        :param defer:
        :param values:
        :param prefetch_related:
        :param select_related:
        :param annotate:
        :param filter:
        :param order_by:
        :param ext_method: use one of  (all, first, distinct)
        :param get_object_or_404_params: specify a dictionary of parameters if you need to pass an object to get_object_or_404(**kwargs)
        :param get: specify a dictionary of parameters if you need to pass an object to get(**kwargs)
        :return:
        """
        annotate = annotate or {}
        filter = filter or {}

        if _object and not model:
            _obj = _object
        elif model and not _object:
            _obj = model.objects
        else:
            raise ValueError

        if values and not defer:
            obj = getattr(_obj, "values")(*values)
        elif defer and not values:
            obj = getattr(_obj, "defer")(*defer).select_related(*select_related)
        else:
            obj = _obj.select_related(*select_related)
        obj = (
            obj.prefetch_related(*prefetch_related)
            .annotate(**annotate)
            .filter(**filter)
            .order_by(order_by)
        )

        if ext_method:
            obj = getattr(obj, ext_method)()

        if get_object_or_404_params:
            obj = get_object_or_404(obj, **get_object_or_404_params)

        if get:
            obj = getattr(obj, "get")(**get)

        return obj

    @classmethod
    def user_create(cls, User, data_dict):
        user = User.objects.create_user(**data_dict)
        user.save()
        return user

    @classmethod
    def get_object(cls, model, data_dict):
        return model.objects.get(**data_dict)

    @classmethod
    def create_or_get(cls, model, data_dict):
        return model.objects.get_or_create(**data_dict)

    @classmethod
    def create_object(cls, model, data_dict):
        return model.objects.create(**data_dict)
