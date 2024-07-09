

from django.core.exceptions import ValidationError
from django.forms import ModelForm, ModelMultipleChoiceField, Form, HiddenInput, Select, ModelChoiceField, CharField

from django.utils import timezone
from django_celery_beat.models import CrontabSchedule

from mailshots.models import Message, Client, MailshotPeriodicTask
from services.general.form_mixins import FormControlMixin


class MessageForm(FormControlMixin, ModelForm):
    """
    Форма сообщения
    """
    class Meta:
        model = Message
        exclude = ["user"]


class ClientsChoseForm(FormControlMixin, Form):
    """
    Форма выбора клиентов
    """
    def __init__(self, choices_queryset, *args, **kwargs):
        """
        Переопределение __init__ для добавления queryset
        """
        super().__init__(*args, **kwargs)
        self.fields["clients"] = ModelMultipleChoiceField(
            queryset=choices_queryset,
        )


class MailshotPeriodicTaskForm(FormControlMixin, ModelForm):
    """
    Форма периодической рассылки
    """
    def __init__(self, user, *args, **kwargs):
        """
        Переопределение __init__ для добавления параметра user
        """
        self.user = user
        super().__init__(*args, **kwargs)

    class Meta:
        model = MailshotPeriodicTask
        fields = ["defined_name", "start_time", "expires", "frequency"]

    def clean_expires(self):
        expires = self.cleaned_data.get("expires")
        start_time = self.cleaned_data.get("start_time")
        if expires is None:
            raise ValidationError(
                "Поле обязательно"
            )
        if expires < timezone.now():
            raise ValidationError(
                "Рассылка не может заканчиваться раньше текущего времени"
            )
        if start_time > expires:
            raise ValidationError(
                "Рассылка не может кончаться раньше, чем начнётся"
            )
        return expires

    def clean_start_time(self):
        start_time = self.cleaned_data.get("start_time")
        if start_time is None:
            raise ValidationError(
                "Поле обязательно"
            )
        return start_time

    def clean(self):
        self._validate_unique = False
        return self.cleaned_data

    def clean_defined_name(self):
        defined_name = self.cleaned_data.get("defined_name")
        obj = self._meta.model.objects.filter(defined_name=defined_name, user=self.user)

        if obj.exists() and obj.exclude(pk=self.instance.pk if self.instance else -1).exists():
            raise ValidationError("У вас уже есть рассылка с таким названием")
        return defined_name


class ClientForm(FormControlMixin, ModelForm):
    """
    Форма клиента
    """
    class Meta:
        model = Client
        exclude = ["user"]

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_email(self):
        email = self.cleaned_data.get("email")

        obj = self._meta.model.objects.filter(email=email, user=self.user)

        if obj.exists() and obj.exclude(pk=self.instance.pk if self.instance else -1).exists():
            raise ValidationError("У вас уже есть клиент с таким email")
        return email


class MailshotDisableForm(FormControlMixin, ModelForm):
    """
    Форма отключения рассылки
    """
    class Meta:
        model = MailshotPeriodicTask
        fields = ["enabled"]
        widgets = {
            "enabled": HiddenInput(),
        }
