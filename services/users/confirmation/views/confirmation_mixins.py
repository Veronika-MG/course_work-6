from django.contrib.auth import login
from django.shortcuts import redirect


class ConfirmValidationViewMixin:
    """
    Класс для интеграции проверки данных валидации в представление
    и реализации механизмов по итогу проверки.

    Валидация работает следующим образом:
    В случае успеха должен запуститься обработчик success_handler
    и вернуть super().dispatch(request, *args, **kwargs)

    В остальных случаях запускаются другие обработчики, которые возвращают редиректы и
    не должны допускать пользователя "внутрь" контроллера


    #########       Все обрабочики должны принимать те же аргументы, что и стандартный метод dispatch
    # Важно #       класса View
    #########


    #########       В связи со спецификой описанного выше механизма проверки данных, данный
    # Важно #       миксин рекомендуется располагать в порядке mro непосредственно перед классом контроллера.
    #########       Это необходимо, так как Access-миксины из стандартного приложения auth используют
                    метод dispatch для своих нужд, который выше описанный миксин может не вызвать
    """
    validator_class = None
    after_login = True
    status_hadler_suffix = "_handler"
    failure_redirect_viewname = None

    def dispatch(self, request, *args, **kwargs):
        """
        Переопределенный метод из стандартного класса View,
        в который добавлена валидация данных ссылки активации
        """
        self.valid = False
        self.validator = self.validator_class.init_by_dispatch_kwargs(request, **kwargs)
        status = self.validator.valid_status()

        return getattr(self, status + self.status_hadler_suffix)(request, *args, **kwargs)

    def success_handler(self, request, *args, **kwargs):
        """
        Обработчик, который по итогу должен вернуть
        super().dispatch(request, *args, **kwargs)
        """
        self.valid = True
        return super().dispatch(request, *args, **kwargs)

    def finish_validation(self):
        """
        Метод завершения процедуры валидации.
        Производит процедуры, которые должны быть произведены по окончанию валидации.
        При переопределении рекомендуется вызывать super-метод.
        Рекомендуется применять непосредственно в последнем дочернем классе в месте, где
        необходимо завершить валидацию.

        """
        self.validator.activate_user()
        self.request = self.validator.del_token_in_request(self.request)

        if self.after_login:
            login(self.request, self.validator.user)

    def failure_handler(self, request, *args, **kwargs):
        """
        Обработчик провала валидации
        """
        return redirect(self.failure_redirect_viewname)

    def substitute_handler(self, request, *args, **kwargs):
        """
        Обработчик замены токена и редиректа на текущий контроллер с
        фальшивым токеном
        """
        self.request = self.validator.save_token(request)
        redirect_url = self.validator.substitute_redirect_url(request)
        return redirect(redirect_url)
