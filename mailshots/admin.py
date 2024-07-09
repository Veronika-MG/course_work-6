from django.contrib import admin
from mailshots.models import Client, Message, Log, MailshotPeriodicTask


# Register your models here.
@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    pass


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    pass


@admin.register(MailshotPeriodicTask)
class MailshotPeriodicTaskAdmin(admin.ModelAdmin):
    fields = ("defined_name",
              "frequency",
              "is_new",
              "clients",
              "message",
              "user",
              "created_at",
              "start_time",
              "expires",
              "crontab",
              "enabled",
              )
    readonly_fields = ("created_at",)


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    pass
