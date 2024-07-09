from datetime import datetime
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages

from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.utils import timezone
from django.views.generic import DetailView, ListView
from django.views.generic.edit import DeleteView, UpdateView, CreateView
from mailshots.tasks import send_mailshot
from mailshots.forms import MessageForm, ClientsChoseForm, ClientForm, MailshotPeriodicTaskForm, MailshotDisableForm

from mailshots.models import Client, MailshotPeriodicTask, Log
from services.general.view_mixins import PKSuccessViewnameMixin, WizardCreateView, WizardUpdateView, \
    SuccessViewnameMixin, ActiveUrlMixin
from services.users import UserBelongedListMixin, UserBelongedObjectTestMixin


##############################################################

# Миксин для логики, общей для создания и редактирования
# рассылки

##############################################################


FORMS = [
    ("message", MessageForm),
    ("clients", ClientsChoseForm),
    ("mailshot_periodic_task", MailshotPeriodicTaskForm),
]

TEMPLATES = {
    "message": "mailshots/wizard/message.html",
    "clients": "mailshots/wizard/clients.html",
    "mailshot_periodic_task": "mailshots/wizard/mailshot_periodic_task.html",
}


class MailshotActiveUrl(ActiveUrlMixin):
    """
    Активный url для рассылки
    """
    active_url = "mailshots"


class ClientActiveUrl(ActiveUrlMixin):
    """
    Активный url для клиента
    """
    active_url = "clients"


class MailshotEditMixin(MailshotActiveUrl):
    """
    Миксин общей логики для mailshot wizard views
    """
    queryset = MailshotPeriodicTask.objects.all()
    form_list = FORMS

    def get_template_names(self):
        return [TEMPLATES.get(self.steps.current)]

    def get_form_kwargs(self, step):
        """
        Добавляет дополнительные аргументы форм
        """
        if step == "clients":
            return {"choices_queryset": Client.objects.filter(user=self.request.user)}
        if step == "mailshot_periodic_task":
            return {"user": self.request.user}
        return {}


# ##################### ########################## ###################### #
# ##################### # Основные представления # ###################### #
# ##################### ########################## ###################### #


class MailshotWizardCreateView(LoginRequiredMixin, MailshotEditMixin, WizardCreateView):
    """
    Последовательное создание рассылки
    """
    extra_context = {"title": "Создание рассылки"}

    def done(self, form_list, **kwargs):
        form_dict = kwargs.get("form_dict")
        message_form = form_dict.get("message")
        clients = form_dict.get("clients").cleaned_data.get("clients")
        mailshot_periodic_task_form = form_dict.get("mailshot_periodic_task")

        with transaction.atomic():
            # message
            message = message_form.save(commit=False)
            message.user = self.request.user
            message.save()

            # создаём основной объект
            self.object = mailshot_periodic_task_form.save(commit=False)

            # заполняем основной объект
            self.object.message = message
            self.object.user = self.request.user
            self.object.enabled = False
            self.object.save()
            self.object.clients.set(clients)

        messages.success(self.request, "Рассылка успешно создана!")
        return HttpResponseRedirect(reverse("mailshots:detail", kwargs={"pk": self.object.pk}))


class MailshotWizardUpdateView(LoginRequiredMixin, UserBelongedObjectTestMixin, MailshotEditMixin, WizardUpdateView):
    """
    Последовательное редактирование рассылки
    """
    extra_context = {"title": "Редактирование рассылки"}

    def get_instance_dict(self):
        return {
            "message": self.object.message,
            "mailshot_periodic_task": self.object
        }

    def get_initial_dict(self):
        return super().get_initial_dict() | {
            "clients": {
                "clients": self.object.clients.all()
            }
        }

    def done(self, form_list, **kwargs):
        form_dict = kwargs.get("form_dict")
        message_form = form_dict.get("message")
        clients = form_dict.get("clients").cleaned_data.get("clients")
        mailshot_periodic_task_form = form_dict.get("mailshot_periodic_task")

        with transaction.atomic():
            # message
            message = message_form.save()

            # Обновляем основной объект
            self.object = mailshot_periodic_task_form.save(commit=False)

            # добавляем связанные объекты
            self.object.message = message
            self.object.clients.set(clients)
            self.object.save()
        messages.success(self.request, "Редактирование рассылки завершено!")
        return HttpResponseRedirect(reverse("mailshots:detail", kwargs={"pk": self.kwargs.get("pk")}))

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs) | {"object": self.object}

    def get_step_url(self, step):
        return reverse(self.url_name, kwargs={'step': step, "pk": self.kwargs.get("pk")})


class BaseMailshotDetailView(MailshotActiveUrl, DetailView):
    """
    Базовое представление для детального просмотра рассылки
    """
    model = MailshotPeriodicTask
    template_name = "mailshots/detail.html"

    def get_status(self):
        if self.object.enabled:
            if self.object.expires < timezone.now():
                return "завершена"
            else:
                return "активна"

        else:
            if self.object.is_new:
                return "создана"
            else:
                return "принудительно остановлена"

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs) | {"status": self.get_status()}


class MailshotDetailView(LoginRequiredMixin, UserBelongedObjectTestMixin, BaseMailshotDetailView):
    """
    Представление для детального просмотра рассылки обычным пользователем
    """
    pass


class MailshotDeleteView(LoginRequiredMixin,
                         SuccessMessageMixin,
                         MailshotActiveUrl,
                         SuccessViewnameMixin,
                         UserBelongedObjectTestMixin,
                         DeleteView):
    """
    Представление удаления рассылки
    """
    model = MailshotPeriodicTask
    template_name = "mailshots/delete.html"
    success_viewname = "mailshots:list"
    success_message = "Рассылка удалена."

    def get_response_kwargs(self):
        return {"status": "created"}


class BaseMailshotListView(MailshotActiveUrl, ListView):
    """
    Базовое представление списка рассылок
    """
    model = MailshotPeriodicTask
    template_name = "mailshots/list.html"

    context_object_name = "mailshots"

    def get_queryset(self):
        """
        Фильтрация по параметру статуса
        """
        status = self.kwargs.get("status")

        match status:
            case "finished": return super().get_queryset().filter(expires__lt=datetime.now(), enabled=True)
            case "enabled": return super().get_queryset().filter(enabled=True)
            case "disabled": return super().get_queryset().filter(enabled=False, is_new=False)
            case _: return super().get_queryset().filter(is_new=True)

    def get_context_data(self, *, object_list=None, **kwargs):
        return (super().get_context_data(object_list=object_list, **kwargs) |
                {"status": self.kwargs.get("status")} |
                {"current": self.kwargs.get("status")}
                )


class MailshotListView(LoginRequiredMixin, UserBelongedListMixin, BaseMailshotListView):
    """
    Представление просмотра списка рассылок для обычного пользователя
    """
    pass


class EnableMailshotUpdateView(LoginRequiredMixin,
                               SuccessMessageMixin,
                               PKSuccessViewnameMixin,
                               MailshotActiveUrl,
                               UserBelongedObjectTestMixin,
                               UpdateView):
    """
    Активация рассылки
    """
    model = MailshotPeriodicTask
    form_class = MailshotPeriodicTaskForm
    success_viewname = "mailshots:detail"
    template_name = "mailshots/enable.html"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.enabled = True
        self.object.is_new = False
        self.object.save()
        messages.info(self.request, "Рассылка активирована!")
        if self.object.send_now:
            send_mailshot.delay(pk=self.object.pk)

        return HttpResponseRedirect(self.get_success_url())

    def get_form_kwargs(self):
        return super().get_form_kwargs() | {"user": self.object.user}


class BaseDisableMailshotUpdateView(MailshotActiveUrl, PKSuccessViewnameMixin, UpdateView):
    """
    Базовое представление деактивации рассылки
    """
    model = MailshotPeriodicTask
    form_class = MailshotDisableForm
    success_viewname = "mailshots:detail"
    template_name = "mailshots/disable.html"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.enabled = False
        self.object.is_new = False
        self.object.save()
        messages.info(self.request, "Рассылка приостановлена")
        return HttpResponseRedirect(self.get_success_url())


class DisableMailshotView(LoginRequiredMixin, UserBelongedObjectTestMixin, BaseDisableMailshotUpdateView):
    """
    Представление деактивации рассылки для обычного пользователя
    """
    pass


# ##################### ######################### ###################### #
# ##################### # Представления клиента # ###################### #
# ##################### ######################### ###################### #


class ClientListView(ClientActiveUrl, LoginRequiredMixin, UserBelongedListMixin, ListView):
    """
    Представление просмотра списка клиентов
    """
    model = Client
    template_name = "mailshots/clients/list.html"


class ClientCreateView(ClientActiveUrl, LoginRequiredMixin, SuccessViewnameMixin, CreateView):
    """
    Создание клиента
    """
    model = Client
    form_class = ClientForm
    template_name = "mailshots/clients/form.html"

    def get_success_viewname(self):
        next_view = self.request.POST.get("next_view")

        if next_view == "one_off":
            return "mailshots:clients_list"
        else:
            return "mailshots:clients_create"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        messages.info(self.request, f"клиент с email {self.object.email} добавлен")
        return HttpResponseRedirect(self.get_success_url())

    def get_form_kwargs(self):
        return super().get_form_kwargs() | {"user": self.request.user}


class ClientUpdateView(ClientActiveUrl,
                       LoginRequiredMixin,
                       SuccessViewnameMixin,
                       SuccessMessageMixin,
                       UserBelongedObjectTestMixin,
                       UpdateView):
    """
    Редактирование клиента
    """
    model = Client
    form_class = ClientForm
    template_name = "mailshots/clients/form.html"
    success_viewname = "mailshots:clients_list"
    success_message = "Клиент обновлён"

    def get_form_kwargs(self):
        return super().get_form_kwargs() | {"user": self.request.user}


class ClientDeleteView(ClientActiveUrl,
                       LoginRequiredMixin,
                       SuccessViewnameMixin,
                       SuccessMessageMixin,
                       UserBelongedObjectTestMixin,
                       DeleteView):
    """
    Удаление клиента
    """
    model = Client
    template_name = "mailshots/clients/delete.html"
    success_viewname = "mailshots:clients_list"
    success_message = "клиент удалён"


class ClientDetailView(ClientActiveUrl, LoginRequiredMixin, UserBelongedObjectTestMixin, DeleteView):
    """
    Просмотр клиента
    """
    model = Client
    template_name = "mailshots/clients/detail.html"


# ##################### ####################### ###################### #
# ##################### # Представления логов # ###################### #
# ##################### ####################### ###################### #


class MailshotInlineQuerysetMixin:
    """
    Миксин дочернего для объекта queryset
    """
    def get_queryset(self):
        mailshot_pk = self.kwargs.get("mailshot_pk")
        queryset = super().get_queryset().filter(mailshot__pk=mailshot_pk)

        return queryset


class BaseLogListView(MailshotActiveUrl, MailshotInlineQuerysetMixin, ListView):
    """
    Базовое представление списка логов
    """
    model = Log
    template_name = "mailshots/logs/list.html"

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs) | {"mailshot_pk": self.kwargs.get("mailshot_pk")}


class LogListView(LoginRequiredMixin, UserBelongedListMixin, BaseLogListView):
    """
    Представление списка логов для обычного пользователя
    """
    pass


class BaseLogDetailView(MailshotActiveUrl, MailshotInlineQuerysetMixin, DetailView):
    """
    Базовое представление детального просмотра лога
    """
    model = Log
    template_name = "mailshots/logs/detail.html"


class LogDetailView(LoginRequiredMixin, UserBelongedObjectTestMixin, BaseLogDetailView):
    """
    Представление просмотра лога для обычного пользователя
    """
    pass


# ##################### ########################### ###################### #
# ##################### # Представления менеджера # ###################### #
# ##################### ########################### ###################### #


class ManagerMailshotListView(PermissionRequiredMixin, BaseMailshotListView):
    """
    Просмотр списка рассылок для менеджера
    """
    permission_required = "mailshots.view_mailshot_periodic_task"


class ManagerMailshotDetailView(PermissionRequiredMixin, BaseMailshotDetailView):
    """
    Детальная информация о рассылке для менеджера
    """
    permission_required = "mailshots.view_mailshot_periodic_task"


class ManagerMailshotDisableUpdateView(PermissionRequiredMixin, BaseDisableMailshotUpdateView):
    """
    Отключение рассылки для менеджера
    """
    permission_required = "mailshots.can_disable"
    success_viewname = "mailshots:manager_detail"
