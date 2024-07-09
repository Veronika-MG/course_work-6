from services.general.messages.messages import BaseMessage
from services.general.messages.senders import EmailSenderMixin
from services.users.confirmation.protectors.encoders import ActivationLinkMixin


class BaseValidationMessage(ActivationLinkMixin, BaseMessage):
    """
    Класс сообщения, обладающий методами для получения
    ссылки активации и контекстом, содержащим ссылку активации и пользователя.
    Обладает методами для рендеринга шаблонов заголовка
    и тела сообщения с общим контекстом.

    Сообщение не может быть отослано.
    Класс является контейнером сообщения валидации
    """
    extra_context: dict = None

    def get_context(self) -> dict:
        """
        Метод получения контекста для шаблонов сообщений валидации
        """
        context = super().get_context()
        validation_context = dict(
            link=self.activation_link,
            user=self.user,
        )

        return context | validation_context


class EmailValidationMessage(EmailSenderMixin, BaseValidationMessage):
    """
    Основной полный класс для сообщения валидации и его отправки.
    Позволяет полностью в себе создавать сообщение валидации и отсылать его
    средствами электронной почты
    """
    def get_message_content(self):
        """
        Описывает получение заголовка и тела сообщения
        """
        return dict(
            subject=self.get_subject(),
            message=self.get_body()
        )

    def get_recipients(self):
        """
        Получает email одного пользователя
        для получения письма валидации
        """
        return [self.user.email]
