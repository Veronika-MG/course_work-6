from django.contrib.auth import get_user_model


User = get_user_model()


class BaseUserProtector:
    """
    Базовый класс для описания механизмов кодирования
    и декодирования данных пользователей для валидации
    """
    def __init__(self, user: User, token=None, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.user: User = user
        self._token = token

