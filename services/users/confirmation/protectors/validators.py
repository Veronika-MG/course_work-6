from django.contrib.auth.tokens import default_token_generator

from services.users.confirmation.protectors.base import BaseUserProtector
from services.general.db.getters import UserSafeGetter


class UserValidator(UserSafeGetter, BaseUserProtector):
    """
    Общий класс для процедур, необходимых для проверки данных валидации.
    Включает в себя методы для сохранения токена в сессии,
    проверки его статуса, его удаления и активации пользователя.
    """
    mask_token: str = "confirm"
    INTERNAL_SESSION_TOKEN: str = "_confirmation_token"

    @classmethod
    def init_by_dispatch_kwargs(cls, request, uidb64, token, **kwargs):
        """
        Инкапсулирует в себе получение пользователя и других объектов, необходимых
        для инициализации класса.
        Для получения аргументов инициализатора используются аргументы метода
        dispatch класса View
        """
        _ = kwargs
        self = cls(user=None, _token=token, session_token=None)
        self.user = self.get_obj_or_none(uidb64=uidb64)
        self.session_token = request.session.get(cls.INTERNAL_SESSION_TOKEN)
        return self

    def __init__(self, user, _token, session_token) -> None:
        super().__init__(user, _token)
        self.session_token = session_token

    def valid_status(self) -> str:
        """
        Метод для проверки статуса токена.
        Возвращает одну из строк статуса по которой позже формируется
        обработчик данного статуса в представлении
        """
        if self.user is not None:
            if self._token == self.mask_token:
                if default_token_generator.check_token(self.user, self.session_token):
                    return "success"
            else:
                return "substitute"
        return "failure"

    def save_token(self, request):
        """
        Метод для сохранения токена в сессии
        """
        request.session.update({self.INTERNAL_SESSION_TOKEN: self._token})
        return request

    def substitute_redirect_url(self, request) -> str:
        """
        Метод подмены токена в пути url для переадресации с целью
        предотвращения кражи токена из заголовка "HTTP-REFERER"
        """
        return request.path.replace(self._token, self.mask_token)

    def del_token_in_request(self, request):
        """
        Метод удаления токена из сессии
        """
        request.session.pop(self.INTERNAL_SESSION_TOKEN, None)
        return request

    def activate_user(self) -> None:
        """
        Метод активации пользователя
        """
        self.user.is_active = True
        self.user.save()
