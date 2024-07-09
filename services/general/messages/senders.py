from typing import Any

from django.conf import settings
from django.core.mail import send_mail

from users.tasks import async_send


class SenderMixin:
    """
    Абстрактный класс для описания методов рассылки сообщения.
    Также описывает методы для получения аргументов рассылки, например,
    контента сообщения и списка получателей, которые стоит описать при
    описании общего для дочернего класса, содержащего также методы сообщения
    """
    def send(self) -> Any:
        """
        Метод для описания непосредственного механизма
        отправки сообщения
        """
        raise NotImplementedError

    def get_send_kwargs(self) -> dict:
        """
        Метод для описания получения аргументов отправки
        сообщения
        """
        raise NotImplementedError


class MessageContentMixin:
    def get_recipients(self) -> list:
        """
        Метод для описания получения списка получателей
        """
        raise NotImplementedError

    def get_message_content(self) -> dict:
        """
        Метод для описания получения контента сообщения:
        например, получение заголовка и тела сообщения
        """
        raise NotImplementedError


class EmailSenderMixin(MessageContentMixin, SenderMixin):
    """
    Специализированный класс для рассылки сообщения средствами
    электронной почты
    """
    from_email: str = None
    extra_email_kwargs: dict | None = None

    def get_send_kwargs(self):
        """
        Получает аргументы отправки письма электронной почтой
        """
        message_content = self.get_message_content()
        kwargs = dict(
            from_email=self.from_email or settings.EMAIL_HOST_USER,
            recipient_list=self.get_recipients(),
            fail_silently=False
        ) | message_content

        kwargs |= self.extra_email_kwargs or {}

        return kwargs

    def asend(self):
        """
        Специализированный метод для отправки сообщения средствами
        электронной почты
        """
        async_send.delay(**self.get_send_kwargs())

    def send(self):
        return send_mail(**self.get_send_kwargs())

    def __call__(self):
        return self.send()
