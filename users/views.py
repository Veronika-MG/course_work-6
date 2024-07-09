from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetConfirmView
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.contrib import messages

from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView, DetailView, ListView

from services.general.view_mixins import PKSuccessViewnameMixin, SuccessViewnameMixin, ActiveUrlMixin
from services.users import UserIsNotAuthenticatedMixin, UserBelongedObjectTestMixin

from django.contrib.auth import get_user_model

from users.forms import RegistrationForm, LoginForm, UserPasswordResetForm, UserSetPasswordForm, UserUpdateForm, \
    DeactivateUserForm

from django.contrib.sites.models import Site
from services.users.confirmation.messages import EmailValidationMessage
from services.users.confirmation.protectors.validators import UserValidator
from services.users.confirmation.views.confirmation_mixins import ConfirmValidationViewMixin
from services.users.confirmation.views.message_mixins import ValidationMessageViewMixin


User = get_user_model()


class UsersActiveUrlMixin(ActiveUrlMixin):
    """
    Миксин активного url пользователей
    """
    active_url = "users"

# Миксины регистрации


class RegistrationMessage(EmailValidationMessage):
    """
    Класс, описывающий отправку сообщение валидации для регистрации
    """
    subject_template_name = "users/email/registration/subject.html"
    body_template_name = "users/email/registration/body.html"

    protocol = "http"
    domain = Site.objects.get_current().domain
    viewname = "users:registration_link"


class RegistrationMessageViewMixin(ValidationMessageViewMixin):
    message_class = RegistrationMessage
    """
    Специальный класс для создания и отправки сообщения валидации
    при регистрации
    """

    def set_user_object(self, form):
        """
        Метод получения объекта при регистрации из
        формы регистрации
        """
        self.object = form.save(commit=False)
        self.object.is_active = False
        self.object.save()


class RegistrationValidationViewMixin(ConfirmValidationViewMixin):
    """
    Класс проверки данных валидации
    при регистрации
    """
    validator_class = UserValidator
    failure_redirect_viewname = "users:registration_confirmation_failed"


# Регистрация


class RegistrationView(UsersActiveUrlMixin,
                       SuccessViewnameMixin,
                       UserIsNotAuthenticatedMixin,
                       RegistrationMessageViewMixin,
                       CreateView):
    """
    Представление регистрации
    """
    model = User
    form_class = RegistrationForm

    template_name = "users/registration/form.html"
    success_viewname = "users:registration_email_sent"


class RegistrationEmailSentTemplateView(UsersActiveUrlMixin, UserIsNotAuthenticatedMixin, TemplateView):
    """
    Представление уведомления об отправке письма
    """
    template_name = "users/registration/email_sent.html"


class RegistrationValidationView(UsersActiveUrlMixin, UserIsNotAuthenticatedMixin, RegistrationValidationViewMixin, TemplateView):
    """
    Представление валидации ссылки активации
    """
    template_name = "users/registration/success.html"

    def success_handler(self, request, *args, **kwargs):
        self.finish_validation()
        return super().success_handler(request, *args, **kwargs)


class RegistrationFailedView(UsersActiveUrlMixin, UserIsNotAuthenticatedMixin, TemplateView):
    """
    Представление для уведомления о провале валидации ссылки
    """
    template_name = "users/registration/failed.html"


# Вход и выход


class UserLoginView(UsersActiveUrlMixin, UserIsNotAuthenticatedMixin, SuccessMessageMixin, LoginView):
    """
    Представление входа
    """
    form_class = LoginForm
    template_name = "users/auth/login_form.html"
    success_message = "Вы успешно вошли"


class LogoutPreview(UsersActiveUrlMixin, LoginRequiredMixin, TemplateView):
    """
    Представление для отображения формы выхода
    """
    template_name = "users/auth/logout_form.html"


class UserLogoutView(LoginRequiredMixin, LogoutView):
    """
    Представление выхода
    """
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        messages.info(request, "Вы успешно вышли")
        return response


# Сброс пароля


class UserPasswordResetView(UsersActiveUrlMixin, UserIsNotAuthenticatedMixin, SuccessViewnameMixin, PasswordResetView):
    """
    Представление форсы сброса пароля
    """
    form_class = UserPasswordResetForm
    template_name = "users/reset/form.html"
    success_viewname = "users:reset_email_sent"

    subject_template_name = "users/email/reset/subject.txt"
    email_template_name = "users/email/reset/mail.html"


class ResetEmailSentTemplateView(UsersActiveUrlMixin, UserIsNotAuthenticatedMixin, TemplateView):
    """
    Представление для уведомления об отправке письма для сброса пароля
    """
    template_name = "users/reset/email_sent.html"


class UserPasswordResetConfirmView(UsersActiveUrlMixin, SuccessViewnameMixin, PasswordResetConfirmView):
    """
    Представление валидации ссылки для сброса пароля и
    установки нового пароля
    """
    form_class = UserSetPasswordForm
    template_name = "users/reset/set_password_form.html"
    success_viewname = "users:reset_complete"
    post_reset_login = True


class ResetCompleteTemplateView(UsersActiveUrlMixin, TemplateView):
    """
    Представление уведомления об успешном восстановлении пароля
    """
    template_name = "users/reset/success.html"


# Остальные контроллеры CRUD


class UserObjectViewGetter:
    """
    Миксин получения пользователя из request
    """
    def get_object(self, queryset=None):
        return self.request.user


class UserUpdateView(LoginRequiredMixin,
                     UsersActiveUrlMixin,
                     UserObjectViewGetter,
                     SuccessMessageMixin,
                     SuccessViewnameMixin,
                     UpdateView):
    """
    Представление редактирование пользователя
    """
    model = User
    form_class = UserUpdateForm
    template_name = "users/update.html"
    success_viewname = "users:detail"
    success_message = "Профиль отредактирован!"


class BaseUserDetailView(UsersActiveUrlMixin, DetailView):
    """
    Базовое представление детального просмотра пользователя
    """
    model = User
    template_name = "users/detail.html"
    context_object_name = "user"


class UserDetailView(LoginRequiredMixin, UserObjectViewGetter, BaseUserDetailView):
    """
    Представление для просмотра текущего авторизованного пользователя
    """
    pass


# ##################### ########################### ###################### #
# ##################### # Представления менеджера # ###################### #
# ##################### ########################### ###################### #


class ManagerDeactivateUserUpdateView(PKSuccessViewnameMixin, UsersActiveUrlMixin, PermissionRequiredMixin, UpdateView):
    """
    Представление деактивации пользователя для менеджера
    """
    model = User
    permission_required = "users.can_deactivate"
    success_viewname = "users:manager_detail"
    form_class = DeactivateUserForm
    template_name = "users/management/deactivate.html"

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.is_active = False
        self.object.save()
        messages.info(self.request, "Пользователь заблокирован.")
        return HttpResponseRedirect(self.get_success_url())


class ManagerUserListView(UsersActiveUrlMixin, PermissionRequiredMixin, ListView):
    """
    Просмотр списка пользователей
    """
    model = User
    permission_required = "users.view_user"
    template_name = "users/management/list.html"


class ManagerUserDetailView(PermissionRequiredMixin, BaseUserDetailView):
    """
    Детальный просмотр пользователя для менеджера
    """
    permission_required = "users.view_user"
    template_name = "users/management/detail.html"
