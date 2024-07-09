"""
Теги статистики по рассылкам
"""
from django import template
from django.utils import timezone

from mailshots.models import MailshotPeriodicTask, Client

register = template.Library()


@register.simple_tag
def mailshots_amount():
    """
    Количество рассылок
    """
    return MailshotPeriodicTask.objects.all().count()


@register.simple_tag
def active_mailshots_amount():
    """
    Количество активных рассылок
    """
    return MailshotPeriodicTask.objects.filter(enabled=True, expires__lt=timezone.now()).count()


@register.simple_tag
def clients_amount():
    """
    Количество клиентов
    """
    return Client.objects.all().order_by("email").distinct("email").count()
