import json
from datetime import timedelta

from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import UniqueConstraint
from django.utils import timezone
from django_celery_beat.models import PeriodicTask, CrontabSchedule

from conf import settings

User = get_user_model()


NULL = dict(
    null=True,
    blank=True
)

CASCADE = dict(
    on_delete=models.CASCADE
)

SET_NULL = dict(
    on_delete=models.SET_NULL
)


class Client(models.Model):
    """
    Клиент рассылки
    """
    email = models.EmailField(verbose_name="email")
    name = models.CharField(max_length=32, **NULL, verbose_name="Имя")
    surname = models.CharField(max_length=32, **NULL,  verbose_name="Фамилия")
    patronymic = models.CharField(max_length=32, **NULL, verbose_name="Отчество")
    comment = models.TextField(**NULL,  verbose_name="Комментарий")
    user = models.ForeignKey(User, **CASCADE, verbose_name="Добавивший пользователь")  # mto
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"
        ordering = ["-created_at"]
        constraints = [
            UniqueConstraint(fields=["email", "user"], name="unique_client_for_user")
        ]

    def __str__(self):
        return self.email


class Message(models.Model):
    """
    Сообщение рассылки
    """
    subject = models.CharField(max_length=256, **NULL, verbose_name="Заголовок")
    body = models.TextField(**NULL,  verbose_name="Содержимое сообщения")
    user = models.ForeignKey(User, **CASCADE,  verbose_name="Создавший пользователь")

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"

    def __str__(self):
        return self.subject


FREQUENCY_CHOICES = [
    ("DAILY", "every day"),
    ("WEEKLY", "every week"),
    ("MONTHLY", "every_month"),
]


class MailshotPeriodicTask(PeriodicTask):
    """
    Модель рассылки
    """
    defined_name = models.CharField(max_length=100, verbose_name="Имя, установленное пользователем")
    frequency = models.CharField(max_length=8, choices=FREQUENCY_CHOICES, verbose_name="Частота рассылки",
                                 default="DAILY",
                                 blank=False)
    is_new = models.BooleanField(default=True,  verbose_name="Рассылка новая")
    clients = models.ManyToManyField(Client, verbose_name="Получатели")  # mtm
    message = models.OneToOneField(Message, **CASCADE,  verbose_name="Сообщение")
    user = models.ForeignKey(User, **CASCADE,  verbose_name="Создана пользователем")  # mto
    created_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            UniqueConstraint(fields=["defined_name", "user"], name="unique_mailshot_name_for_user")
        ]
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        ordering = ["-created_at"]

        permissions = [
            ("can_disable", "can disable mailshots"),
        ]

    def __str__(self):
        return self.defined_name

    def alter_crontab(self, start_at):
        """
        Метод для определения расписания crontab
        по времени начала
        """
        if self.crontab:
            crontab = self.crontab
        else:
            crontab = CrontabSchedule()

        crontab.minute = start_at.minute
        crontab.hour = start_at.hour
        crontab.day_of_month = '*'
        crontab.month_of_year = '*'
        crontab.day_of_week = '*'

        if self.frequency == "WEEKLY":
            crontab.day_of_week = start_at.weekday()
        elif self.frequency == "MONTHLY":
            crontab.day_of_month = start_at.month
        crontab.save()

        self.crontab = crontab

    @property
    def send_now(self):
        return self.start_time < timezone.now()

    def save(self, *args, **kwargs):
        self.alter_crontab(self.start_time)
        self.name = f"mailshot_-1"
        self.kwargs = json.dumps({"pk": -1})
        super().save(*args, **kwargs)
        self.task = settings.MAILSHOT_TASK_NAME
        self.kwargs = json.dumps({"pk": self.pk})
        self.name = f"mailshot_{self.pk}"
        super().save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False):
        ret = super().delete(using=None, keep_parents=False)
        self.crontab.delete()
        self.message.delete()
        return ret


class Log(models.Model):
    """
    Логи рассылки
    """
    class Status(models.TextChoices):
        OK = "OK"
        FAIL = "FD"

    class Meta:
        verbose_name = "Информация об отправке"
        verbose_name_plural = "Информация об отправках"

    def __str__(self):
        return f"{self.mailshot.defined_name}_{self.mailshot_datetime}"

    mailshot = models.ForeignKey(MailshotPeriodicTask, **CASCADE, verbose_name="Рассылка")  # mto
    mailshot_datetime = models.DateTimeField(auto_now=True, verbose_name="Дата отправки")
    status = models.CharField(choices=Status, max_length=2, verbose_name="Статус отправки")
    response = models.CharField(max_length=16, verbose_name="Ответ сервиса отправки")
    user = models.ForeignKey(User, **CASCADE, verbose_name="Создана пользователем")  # mto
