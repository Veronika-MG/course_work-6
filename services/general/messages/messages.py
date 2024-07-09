from typing import Any

from django.template import loader


class RawMessage:
    """
    Описывает сырое нефункциональное сообщение, содержит в себе поля
    имён шаблонов для заголовка и тела сообщения
    """
    subject_template_name: str = None
    body_template_name: str = None


class MessageContextMixin:
    """
    Миксин контекста сообщения
    """
    extra_context = None

    def get_context(self):
        extra_context = self.extra_context or {}
        return extra_context | {}


class BaseMessage(MessageContextMixin, RawMessage):
    """
    Базовый класс сообщения
    """
    def get_subject(self, oneline: bool = True) -> str:
        """
        Метод рендерит шаблон с заголовком, интерполируя контекст в шаблон.
        Возвращает строку заголовка.

        oneline = True:
            заголовок возвращается без переноса строк
        oneline = False:
            заголовок возвращается как в файле, с переносами строк
        """
        subject = loader.render_to_string(self.subject_template_name, self.get_context())

        if oneline:
            subject = "".join(subject.splitlines())

        return subject

    def get_body(self) -> str:
        """
        Метод рендерит шаблон с телом сообщения, интерполируя контекст в шаблон.
        Возвращает строку тела сообщения.
        """
        return loader.render_to_string(self.body_template_name, self.get_context())