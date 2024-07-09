from typing import Any, Callable

from django.db.models import Model
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils.http import urlsafe_base64_decode


User = get_user_model()


class SingleKwargSafeGetter:
    """
    Позволяет описывать и специализировать методы для безопасного получения объекта модели по
    одному ключевому аргументу с помощью единого метода get_obj_or_none, в случае возникновения ошибки метод
    возвращает None. Дополнительные для обработки ошибки можно указывать в extra_exceptions.
    Для прописывания специфических алгоритмов получения описываются методы, имя которых соответствует шаблону:
    handler_starts_with + <имя ключевого аргумента>, например, для базового класса и поиска по pk нужно описать
    метод с именем get_by_pk
    """
    handler_starts_with: str = "get_by_"
    model: Model = None
    extra_exceptions: tuple = ()

    def get_handler(self, k: str) -> Callable:
        """
        Метод для получения обработчика поиска по имени ключевого аргумента
        """

        handler_name: str = self.handler_starts_with + k

        try:
            handler: Callable = getattr(self, handler_name)
        except AttributeError:
            raise AttributeError(f"Нет обработчика для поиска по {k}")

        return handler

    @staticmethod
    def check_kwargs(kwargs: dict) -> dict:
        """
        Проверяет единственность ключа
        """
        if len(kwargs) != 1:
            raise ValueError("метод принимает ровно один kw параметр")
        return kwargs

    def get_obj_or_none(self, **kv_pair: Any) -> Model | None:
        """
        Основной метод
        """
        kv_pair: dict = self.check_kwargs(kv_pair)
        k, *_ = kv_pair

        try:
            obj: Model | None = self.get_handler(k)(**kv_pair)
        except (TypeError, ValueError, OverflowError, *self.extra_exceptions):
            obj = None

        return obj


class UserSafeGetter(SingleKwargSafeGetter):
    """
    Специализированный для пользователя класс SingleKwargSafeGetter.

    В классе определены методы для поиска по uidb64 и email.
    В случае необходимости можно унаследоваться от данного класса и добавить
    дополнительные методы для поиска объектов пользователя по ключам.
    В случае других моделей и изменения базовых методов
    лучше наследоваться от SingleKwargSafeGetter
    """
    model = User
    handler_starts_with: str = "get_user_by_"
    extra_exceptions = (model.DoesNotExist, ValidationError)

    def get_user_by_uidb64(self, uidb64: str) -> User:
        """
        Получение пользователя по uidb64
        """
        uid: bytes = urlsafe_base64_decode(uidb64)
        user: User = self.model.objects.get(pk=uid)
        return user

    def get_user_by_email(self, email: str) -> User:
        """
        Получение пользователя по email
        """
        user = self.model.objects.get(email=email)
        return user


user_safe_getter = UserSafeGetter()
