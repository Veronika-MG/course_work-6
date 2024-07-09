from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.views import View
from django.views.generic.detail import SingleObjectMixin
from formtools.wizard.views import NamedUrlSessionWizardView
from django.core.cache import cache

from conf import settings


class ActiveUrlMixin:
    active_url: str | None = None
    active_url_key = "active_url"

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs) | {self.active_url_key: self.active_url}


##############################################################

# Кастомные представления для получения URL

##############################################################


class SuccessViewnameMixin:
    success_viewname = None

    def get_response_args(self):
        return ()

    def get_response_kwargs(self):
        return {}

    def get_success_viewname(self):
        raise NotImplementedError

    def get_success_url(self):
        return reverse(self.success_viewname or self.get_success_viewname(),
                       args=self.get_response_args(),
                       kwargs=self.get_response_kwargs())


class PKSuccessViewnameMixin(SuccessViewnameMixin):
    def get_response_kwargs(self):
        return {self.pk_url_kwarg: self.object.pk}


##############################################################

# Миксины для методов, переопределяющих механизмы получения
# атрибутов. Позволяют получать атрибуты из экземпляра класса,
# не наследуя их от класса

##############################################################


class InstanceDictMethodMixin:
    def get_instance_dict(self):
        raise NotImplementedError


class InitialDictMethodMixin:
    def get_initial_dict(self):
        return self.initial_dict


##############################################################

# Модифицированные WizardView для реализации пошагового
# механизма CRUD сложной модели

##############################################################


class WizardUpdateView(InitialDictMethodMixin, InstanceDictMethodMixin, SingleObjectMixin, NamedUrlSessionWizardView):
    """
    wizard view для редактирования объекта
    """
    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object(self.queryset)
        self.instance_dict = self.get_instance_dict()
        self.initial_dict = self.get_initial_dict()
        return super().dispatch(request, *args, **kwargs)


class WizardCreateView(NamedUrlSessionWizardView):
    """
    wizard view для создания объекта
    """
    def dispatch(self, request, *args, **kwargs):
        self.object = None
        return super().dispatch(request, *args, **kwargs)


class CachedQuerySetMixin:
    """
    Миксин кеширование queryset
    """
    cache_lifetime = 60
    cache_key = None

    def get_cahce_key(self):
        return self.model.__class__.__name__.lower() + "_queryset"

    def get_queryset(self):
        if settings.CACHE_ENABLED:
            key = self.cache_key or self.get_cahce_key()
            queryset = cache.get(key)

            if queryset is None:
                queryset = super().get_queryset()
                cache.set(key, queryset)
                return queryset

            return queryset
        return super().get_queryset()
