from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from services.users.confirmation.protectors.base import BaseUserProtector


class UserEncoder(BaseUserProtector):
    """
    Класс с описанием механизмов кодирования данных для валидации пользователя
    """
    save_single_token: bool = True

    @property
    def uidb64(self) -> str:
        """
        Метод, вычисляющий uidb64 по pk пользователя
        """
        return urlsafe_base64_encode(force_bytes(self.user.pk))

    @property
    def token(self) -> str:
        """
        Метод генерациии токена для пользователя,
        может кешировать результат для уникализации токена на один объект
        """
        if self._token is not None:
            return self._token

        token = default_token_generator.make_token(self.user)
        if self.save_single_token:
            self._token = token
        return token


class ActivationLinkMixin(UserEncoder):
    """
    Класс для генерации ссылки активации
    """
    protocol: str = None
    domain: str = None
    viewname: str = None
    extra_url_kwargs: dict | None = None

    def get_url_kwargs(self) -> dict:
        """
        Метод для получения аргументов для url-path
        """
        main_url_kwargs = dict(
            uidb64=self.uidb64,
            token=self.token
        )
        extra_url_kwargs = self.extra_url_kwargs or {}
        return main_url_kwargs | extra_url_kwargs

    def get_viewname(self) -> str:
        """
        Получение имени представления для
        ссылки активации
        """
        return self.viewname

    def make_url(self) -> str:
        """
        Интерполирует полученные аргументы в
        шаблон url-path
        """
        url_kwargs = self.get_url_kwargs()
        viewname = self.get_viewname()
        return reverse(viewname, kwargs=url_kwargs)

    def get_protocol(self) -> str:
        """
        Получение протокола для ссылки активации
        """
        return self.protocol

    def get_domain(self) -> str:
        """
        Получение домена для ссылки активации
        """
        return self.domain

    @property
    def activation_link(self) -> str:
        """
        Основной метод класса.
        Возвращает абсолютную ссылку активации для пользователя,
        переданного в init
        """
        domain = self.get_domain()
        protocol = self.get_protocol()
        url = self.make_url()
        return f"{protocol}://{domain}{url}"
