from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied


class UserIsNotAuthenticatedMixin(UserPassesTestMixin):
    """
    Класс, проверяющий, что пользователь не вошёл в систему
    """
    def test_func(self):
        return not self.request.user.is_authenticated


#########################################

# Миксины для защиты данных пользователей

#########################################


class UserBelongedListMixin:
    """
    Миксин, фильтрующий queryset, оставляет только объекты,
    принадлежащие текущему пользователю
    """
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)


class ObjectTestMixin:
    """
    Миксин для проверки объекта сразу после его получения
    """
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if self.test_object(obj):
            return obj
        raise PermissionDenied

    def test_object(self, obj):
        raise NotImplementedError


class UserBelongedObjectTestMixin(ObjectTestMixin):
    """
    Проверка объекта на принадлежность
    текущему пользователю
    """
    def test_object(self, obj):
        return obj.user == self.request.user
