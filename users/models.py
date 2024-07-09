from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Модель пользователя без поля username
    и с дополнительными полями
    """
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

        permissions = [
            ("can_deactivate", "can deactivate users"),
        ]

    username = None
    email = models.EmailField(
        verbose_name='почта',
        unique=True
    )
    avatar = models.ImageField(
        verbose_name="Аватар",
        upload_to="users/avatars/",
        default="users/avatars/default/default.svg"
    )
    telephone_number = models.CharField(
        max_length=20,
        verbose_name="Номер телефона",
        unique=True,
        null=True,
        blank=True
    )

    def __str__(self):
        return getattr(self, self.USERNAME_FIELD)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
